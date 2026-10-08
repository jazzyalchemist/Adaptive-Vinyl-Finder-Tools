#!/usr/bin/env python3
"""Package only public source allowlist; never recurse into private state."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parent
TOOLS={'Catalog-Exporter':'catalog_export.py','Memory-Matrix':'memory_matrix.py','Experience-Explorer':'experience_explorer.py','Record-Watchlist':'record_watchlist.py','Site-Finder':'site_finder.py'}

def public_files():
    paths=[ROOT/p for p in ['README.md','LICENSE','vinyl_suite.py','build_packages.py','Control-Hub.html','AI-Start-Here.md','AI-Reuse-Manual.md','.gitignore']]
    paths += [ROOT/p for p in TOOLS.values()]
    for directory in ['docs','prompts','templates','tests','legacy','.github']:
        paths += [p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    return sorted(paths)

def manual():
    files=[ROOT/'README.md']+sorted((ROOT/'docs').glob('*.md'))+sorted((ROOT/'prompts').glob('*.md'))
    text='# Adaptive Vinyl Finder — complete AI reuse manual\n\nCanonical source documents follow in full. Read module boundaries and capabilities honestly.\n\n'
    for p in files: text+='\n\n---\n\nSource: '+str(p.relative_to(ROOT))+'\n\n'+p.read_text()
    (ROOT/'AI-Reuse-Manual.md').write_text(text,encoding='utf-8')
    (ROOT/'AI-Start-Here.md').write_text((ROOT/'prompts/BOOTSTRAP.md').read_text(),encoding='utf-8')

def package(name, paths):
    dist=ROOT/'dist'; dist.mkdir(exist_ok=True)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with zipfile.ZipFile(dist/(name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            info=zipfile.ZipInfo(str(p.relative_to(ROOT)),date_time=(2026,10,8,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())
        if name in TOOLS:
            start=f'# {name}\n\nStart with `{TOOLS[name]}` and its `--help`. This package includes the complete shared system so modules interoperate. Use one private memory path across modules. Read README and AI-Start-Here.md before AI use.\n'
            z.writestr('START-THIS-MODULE.md',start)
            manifest['START-THIS-MODULE.md']=hashlib.sha256(start.encode()).hexdigest()
        z.writestr('PACKAGE-MANIFEST.json',json.dumps({'version':'2.0.0','sha256':manifest},indent=2))

def main():
    manual(); paths=public_files()
    package('Adaptive-Vinyl-Finder-Toolkit',paths)
    # Each module remains independently usable with shared dependencies and all prompts.
    for name in TOOLS: package(name,paths)
    print(json.dumps({'packages':[str(p) for p in sorted((ROOT/'dist').glob('*.zip'))],'source_files':len(paths)},indent=2))

if __name__=='__main__': main()
