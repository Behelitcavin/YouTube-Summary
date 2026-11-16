# YouTube 요약기

YouTube 영상의 자막을 가져와 요약하고, 영상이나 오디오를 내려받고, 요약을 Markdown으로 보관하는 로컬 도구입니다.

| 탭 | 할 수 있는 일 |
| --- | --- |
| **요약** | 영상 자막을 가져오거나 텍스트를 붙여넣고, 한국어·일본어·영어로 핵심 요약 또는 상세 정리를 만듭니다. |
| **다운로드** | 권한이 있는 영상을 MP4, 단일 스트림 또는 MP3로 PC에 저장합니다. |
| **아카이브** | 요약과 원본 자막을 Markdown으로 보관하고, 제목으로 찾아 다시 내려받습니다. |

## 설치 및 실행

1. Python 3.11 이상과 [Deno](https://docs.deno.com/runtime/getting_started/installation/)를 설치합니다. Deno 대신 yt-dlp가 지원하는 Node.js 버전도 사용할 수 있습니다. 자바스크립트 런타임은 [YouTube 자막과 다운로드에 필요](https://github.com/yt-dlp/yt-dlp/wiki/EJS)합니다.
2. 1080p MP4 병합이나 MP3 추출을 사용하려면 [FFmpeg](https://ffmpeg.org/download.html)를 설치하고 PATH에 추가합니다.
3. 로컬 요약을 사용하려면 [Ollama](https://ollama.com/download)를 시작하고 `ollama pull qwen3.5:9b`를 실행합니다. 설치한 다른 모델 이름을 앱에서 입력해도 됩니다.
4. Windows에서는 `start.bat`을 실행합니다. 처음에는 가상환경과 필수 패키지를 설치합니다. 브라우저에서 [http://127.0.0.1:8514](http://127.0.0.1:8514)를 엽니다.

macOS·Linux 또는 수동 설치:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

## 사용법

1. **요약**에서 영상 링크를 입력하고 **자막 가져오기**를 누릅니다. 자막을 가져올 수 없으면 준비한 텍스트를 붙여넣으세요.
2. 언어와 방식을 선택하고 **요약 만들기**를 누릅니다. 기본 엔진인 Ollama는 자막을 PC 내에서 처리합니다.
3. 요약을 바로 내려받거나 **아카이브에 저장**합니다. 결과는 `data/archives/`, 영상은 `data/downloads/`에 저장됩니다. 데이터의 기본 위치를 바꾸려면 `YT_SUMMARY_DATA` 환경변수를 설정하세요.

Gemini를 사용하려면 **요약 엔진 → Gemini**를 선택하고 사용 가능한 모델 이름과 키를 입력합니다. 환경변수 `GEMINI_MODEL`과 `GEMINI_API_KEY`를 사용할 수도 있습니다. Gemini는 선택한 경우에만 자막을 Google로 보내며, 키를 디스크에 저장하지 않습니다.

YouTube에서 자막을 제공하지 않거나 자동화 접근을 제한하는 영상은 가져오기가 실패할 수 있습니다. 접근 문제가 생기면 Deno 설치를 확인하고 같은 가상환경에서 `python -m pip install -U "yt-dlp[default]"`로 업데이트하세요.

[MIT 라이선스](LICENSE)
