"""Create browser playback derivatives; retain the verified lossless evidence."""
import hashlib,json,subprocess
from pathlib import Path

def main():
 data=json.loads(Path('evidence/evaluation_current.json').read_text())
 for row in data['results']:
  for a in row['audio']:
   src=Path(a['path']);dst=src.with_suffix('.mp3')
   if not dst.exists():subprocess.run(['ffmpeg','-v','error','-i',str(src),'-c:a','libmp3lame','-b:a','64k',str(dst)],check=True)
   a.update(playback_path=str(dst),playback_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),playback_format='MP3 listening derivative; FLAC is the lossless evidence')
 Path('evidence/evaluation_current.json').write_text(json.dumps(data,indent=2)+'\n')
 print('Wrote 38 MP3 listening derivatives; lossless sources unchanged')
if __name__=='__main__':main()
