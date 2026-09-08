import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
const coreDir=path.resolve('.claude/skills/_core/deliberation/engine');
const PROFILE=path.resolve('.claude/skills/proposal-deliberation/profile.ts');
const profile=await readFile(PROFILE,'utf8');
// The profile now lives with the skill, not inside the engine, so the core needs
// no exemption: NO file under `_core/` may name a domain, this one included.
// Whatever a domain calls itself, it says so once, and the lock reads those values
// back out rather than naming a project here -- a later domain is held to the same
// rule without this file being edited to know about it.
const declared=[...profile.matchAll(/^\t(?:deriveBase|baseLabel|baseLabelLong|exampleSlug): "([^"]+)",$/gm)].map(m=>m[1]);
const names=[...(profile.match(/^\tnames: \[([^\]]*)\],$/m)?.[1]??'').matchAll(/"([^"]+)"/g)].map(m=>m[1]);
// Phase 1.5 (change 2/3, extended lock): a SECOND, core-only scan surface, reading
// `artifact.{stem, directory, sidecarRoot}` off this same profile -- never added to the
// `declared`/`names` list above, which the SUITE scan below also uses: a node fixture must
// legitimately write real `proposals/research-concept-...` files, and every one of them
// would read as a leak if `stem`/`directory` joined that shared list. `sidecarRoot` is
// matched WITH its leading dot (`.proposal-deliberation`) on purpose: without the dot this
// scan goes red on `PARSER_VERSION` ('proposal-deliberation/1'), the
// `sdd/proposal-deliberation-*` design citations, and the `proposal-deliberation-${uuid}`
// operation-id factories -- none of which is the sidecar namespace.
const artifactDeclared=[...profile.matchAll(/^\t\t(?:directory|stem|sidecarRoot): "([^"]+)",$/gm)].map(m=>m[1]);
const coreFiles=(await readdir(coreDir,{recursive:true,withFileTypes:true}))
	.filter(e=>e.isFile()&&(e.name.endsWith('.ts')||e.name.endsWith('.mjs')))
	.map(e=>path.join(e.parentPath??e.path,e.name));
const sources=await Promise.all(coreFiles.map(async file=>[path.relative(coreDir,file),await readFile(file,'utf8')]));
// The node suite is a guarded surface too, and until now nothing held it.
// The Python-side floor (`FORGE_VOCABULARY_FLOOR`, walked by
// `tests/test_proposal_implementation.py`) covers a skill's SKILL.md,
// references/, assets/ and scripts/ and stops there deliberately:
// `test_the_tests_stay_unguarded_and_it_is_measured` asserts the exclusion,
// because `test_remote_execution.py` names one hosted service hundreds of times
// and legitimately so. That argument does not reach here -- no `.mjs` test ships
// an adapter for a named subject -- so a domain name in a fixture is a leak with
// no exemption behind it. Rather than write a second floor in a second language,
// this scans the node suite with the values the profile already declares: one
// definition, two surfaces. It scans itself too, and holds, because it reads
// every value it checks instead of spelling one.
const suiteDir=path.resolve('tests');
const suiteSources=await Promise.all((await readdir(suiteDir,{recursive:true,withFileTypes:true}))
	.filter(e=>e.isFile()&&e.name.endsWith('.mjs'))
	.map(async e=>{const file=path.join(e.parentPath??e.path,e.name);return[path.relative(suiteDir,file),await readFile(file,'utf8')];}));
test('the profile declares its values and the names behind them',()=>{assert.equal(declared.length,4,`expected 4 declared values, found ${declared.length}`);assert.ok(names.length>0,'the profile declares no domain name, so the lock below would pass vacuously');for(const value of[...declared,...names])assert.notEqual(value.trim(),'');});
test('every declared name really is this domain speaking',()=>{const unused=names.filter(n=>!declared.some(v=>v.toLowerCase().includes(n.toLowerCase()))&&!profile.toLowerCase().includes(n.toLowerCase()));assert.deepEqual(unused,[],'a name no profile value contains is not this domain naming itself');});
test('no file in the shared core names a domain',()=>{
	assert.ok(sources.length>40,`expected the whole engine, scanned ${sources.length}`);
	const leaks=[];
	for(const[rel,source]of sources){const lower=source.toLowerCase();
		// Composed values catch the exact strings; `names` catches the same proper
		// noun re-spelled -- lowercased inside a slug, say, which is how the first
		// sweep of this engine left a residue behind.
		for(const value of declared)if(source.includes(value))leaks.push(`${rel} spells ${JSON.stringify(value)}`);
		for(const name of names)if(lower.includes(name.toLowerCase()))leaks.push(`${rel} names ${JSON.stringify(name)}`);}
	assert.deepEqual([...new Set(leaks)],[],'the core must read these off the host-chosen profile, never spell them');
});
test('the profile declares its artifact namespace values (directory, stem, sidecarRoot)',()=>{
	assert.equal(artifactDeclared.length,3,`expected 3 declared artifact values (directory, stem, sidecarRoot), found ${artifactDeclared.length}`);
	for(const value of artifactDeclared)assert.notEqual(value.trim(),'');
	assert.ok(artifactDeclared.some(v=>v.startsWith('.')),'sidecarRoot must be declared WITH its leading dot, or the core-only scan below cannot tell it apart from the bare word "proposal-deliberation" legitimately used elsewhere in core');
});
test('no file in the shared core spells the artifact namespace',()=>{
	assert.ok(sources.length>40,`expected the whole engine, scanned ${sources.length}`);
	const leaks=[];
	for(const[rel,source]of sources){
		// Zero exemptions, including this file's own module: `artifact-naming.ts` reads
		// `DOMAIN.artifact` back out at runtime, it never spells the literal values itself.
		for(const value of artifactDeclared)if(source.includes(value))leaks.push(`${rel} spells ${JSON.stringify(value)}`);
	}
	assert.deepEqual([...new Set(leaks)],[],'core must read the managed directory/stem/sidecar-root off the host-chosen profile, never spell them');
});
test('no test in the node suite names a domain either',()=>{
	assert.ok(suiteSources.length>30,`expected the whole node suite, scanned ${suiteSources.length}`);
	// Named rather than counted: the file that held 256 of these occurrences is
	// the one a future glob change would most easily drop out of the surface.
	for(const required of['proposal-workspace.test.mjs','proposal-deliberation-v2-source-routing.test.mjs','proposal-deliberation-domain-profile-lock.test.mjs'])
		assert.ok(suiteSources.some(([rel])=>rel===required),`${required} is not in the scanned surface`);
	const leaks=[];
	for(const[rel,source]of suiteSources){const lower=source.toLowerCase();
		for(const value of declared)if(source.includes(value))leaks.push(`${rel} spells ${JSON.stringify(value)}`);
		for(const name of names)if(lower.includes(name.toLowerCase()))leaks.push(`${rel} names ${JSON.stringify(name)}`);}
	assert.deepEqual([...new Set(leaks)],[],'a fixture must read these off the profile too: a general forge does not shape its tests around one research project');
});
test('no document tells a reader to run the bare core',async()=>{
	// The core fails closed without a profile, so an instruction to invoke its
	// cli.mjs directly is an instruction that errors. Every documented entry point
	// must be a skill's own launcher, which supplies the profile. This nearly
	// shipped: the path rewrite that moved the engine updated these commands to the
	// new location and left them pointing at an engine that now refuses.
	const docs=['.claude/skills/proposal-deliberation/SKILL.md','.claude/skills/proposal-deliberation/references/usage.md','.claude/skills/proposal-implementation/SKILL.md','.claude/skills/proposal-implementation/references/usage.md','.claude/skills/experimental-deliberation/SKILL.md','.claude/skills/experimental-deliberation/references/usage.md','README.md'];
	for(const doc of docs){
		const text=await readFile(path.resolve(doc),'utf8').catch(()=>null);
		if(text===null) continue;
		assert.equal(/_core\/deliberation\/engine\/cli\.mjs/.test(text),false,`${doc} invokes the core directly, which refuses without a profile`);
	}
});
test('the core refuses to serve a domain it was not given',async()=>{
	const resolver=await readFile(path.join(coreDir,'domain-profile.ts'),'utf8');
	assert.match(resolver,/DELIBERATION_DOMAIN_PROFILE_REQUIRED/,'no profile must be a refusal, not a default');
	// The half-spelled base filename that used to stand here was itself a
	// residue: the core scan above already refuses every declared value in this
	// very file, so naming one bought nothing and cost the lock its own clean
	// bill of health under the suite scan.
	assert.equal(/proposalDeliberationProfile/.test(resolver),false,'the resolver must carry no domain of its own');
});
