"""Build a local private audit bundle from preserved historical sources. No network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid
import wave
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence_trial import import_log, private_write
from run_suite import GUARD
from report import render


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--historical-audio-dir', type=Path)
    args = ap.parse_args()
    folder = Path('runs') / ('audit-bundle-' + uuid.uuid4().hex)
    folder.mkdir(parents=True, mode=0o700); os.chmod(folder, 0o700)
    records = []
    sources = {p.name: p for p in Path('evidence/logs').glob('*.jsonl')}
    missing_sources = []
    for report_path in sorted(Path('evidence').glob('report_*.json')):
        private_write(folder/report_path.name, report_path.read_bytes())
        for row in json.loads(report_path.read_text())['results']:
            name = Path(row['run']).name
            if name not in sources:
                candidate = args.historical_audio_dir / name if args.historical_audio_dir else None
                if candidate and candidate.is_file():
                    sources[name] = candidate
                else:
                    missing_sources.append({'report': report_path.name, 'run': row['run']})
    private_write(folder/'missing-sources.json', missing_sources)
    for source in sorted(sources.values()):
        target = json.loads(Path('targets/meridian_lax.json' if source.name.startswith('lax_') else 'targets/meridian.json').read_text())
        hardened = source.name.startswith('hardened_')
        if hardened: target['agent']['system_prompt'] += GUARD
        imported = import_log(source, target, folder/'trials', origin='historical_archive_configuration_reconstructed_not_authenticated',
                              defense_changes=GUARD if hardened else 'none recorded')
        result = json.loads((imported/'result.json').read_text())
        result.update(name=source.stem, attack=source.stem, **{'class': 'historical', 'goal': 'Reassess archived events without claiming completed coverage'})
        private_write(imported/'review.html', render({'target': target['id'], 'results': [result]}).encode())
        records.append({'source': str(source), 'trial_id': imported.name, 'finding_verdict': result['verdict'],
                        'evaluation_verdict': result['evaluation_verdict'], 'completion_state': result['completion_state']})
    audio = []
    if args.historical_audio_dir:
        dest = folder/'historical-audio'; dest.mkdir(mode=0o700)
        for path in sorted(args.historical_audio_dir.glob('*.wav')):
            source_log = sources.get(path.stem + '.jsonl')
            original_log = path.with_suffix('.jsonl')
            if source_log is None or not source_log.exists() or not original_log.exists() or source_log.read_bytes() != original_log.read_bytes():
                continue
            with wave.open(str(path), 'rb') as w:
                meta = {'channels': w.getnchannels(), 'sample_rate': w.getframerate(),
                        'seconds': w.getnframes()/w.getframerate()}
            private_write(dest/path.name, path.read_bytes())
            audio.append({'file': 'historical-audio/'+path.name, 'source_log': str(source_log),
                          'provenance': 'existing_local_capture_original_log_matches_archive',
                          'limitation': 'legacy_generated_audio_mix_delivery_and_timing_not_certified', **meta})
    private_write(folder/'archive-reassessment.json', records)
    private_write(folder/'audio-inventory.json', audio)
    for source in [*Path('audit').glob('*.md'), Path('audit/test-results.txt'), Path('audit/changed-files.txt')]:
        private_write(folder/source.name, source.read_bytes())
    private_write(folder/'baseline-reproductions.json', Path('audit/baseline-reproductions.json').read_bytes())
    private_write(folder/'bundle-manifest.json', {'schema_version': 1, 'scope': 'offline_audit_not_new_provider_evaluation',
        'files': {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in folder.rglob('*') if p.is_file()}})
    print(folder.resolve())
    print(json.dumps({'historical_logs': len(records), 'historical_audio_files': len(audio),
                      'new_paid_trials': 0, 'completed_evaluation_trials': sum(r['completion_state']=='complete' for r in records)}))

if __name__ == '__main__': main()
