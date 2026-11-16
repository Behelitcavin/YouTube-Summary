"""Local Streamlit application. Start it with python run.py."""
import os
import re

import streamlit as st

from yt_core import (
    ARCHIVES, DOWNLOADS, archive_items, archive_summary, download_video,
    fetch_transcript, summarize, video_url,
)

st.set_page_config(page_title="YouTube 요약기", page_icon="▶️", layout="centered")
st.title("YouTube 요약기")
st.caption("자막을 읽고 요약한 뒤, 원하는 결과를 PC에 보관하세요.")


def plain_error(error):
    return re.sub(r"\x1b\[[0-9;]*m", "", str(error))[:900]


summary_tab, download_tab, archive_tab = st.tabs(["요약", "다운로드", "아카이브"])

with summary_tab:
    st.subheader("자막과 요약")
    url = st.text_input("YouTube 영상 URL", key="summary_url", placeholder="https://www.youtube.com/watch?v=…")
    left, right = st.columns([2, 1])
    subtitle_language = left.selectbox("자막 언어", ["auto", "ko", "ja", "en"],
                                      format_func=lambda value: {"auto": "자동 (영상 원어 우선)", "ko": "한국어", "ja": "일본어", "en": "영어"}[value])
    if right.button("자막 가져오기", width="stretch"):
        st.session_state.pop("summary_result", None)
        st.session_state["transcript"] = ""
        st.session_state["caption_info"] = {}
        try:
            with st.spinner("YouTube 자막을 가져오는 중…"):
                info = fetch_transcript(url, subtitle_language)
                st.session_state["caption_info"] = info
                st.session_state["transcript"] = info["text"]
        except Exception as error:
            st.error(plain_error(error))
    info = st.session_state.get("caption_info") or {}
    if info:
        st.caption(f'{info["title"]} · {info["source"]}')
    transcript = st.text_area("요약할 자막", key="transcript", height=200,
                              placeholder="영상 자막을 가져오거나, 준비한 자막 텍스트를 직접 붙여넣으세요.")
    with st.form("summary_settings"):
        left, right = st.columns(2)
        provider = left.selectbox("요약 엔진", ["Ollama", "Gemini"])
        language = right.selectbox("출력 언어", ["한국어", "日本語", "English"])
        model = st.text_input("모델 이름 (선택)", placeholder="Ollama 기본: qwen3.5:9b · Gemini는 모델 이름 입력")
        with st.expander("Gemini로 요약할 때"):
            api_key = st.text_input("Gemini API 키 (선택)", type="password")
            st.caption("Gemini를 선택하면 자막이 Google로 전송됩니다. 키는 파일에 저장되지 않습니다. 요금은 사용 중인 Google 계정의 설정을 따릅니다.")
        style = st.radio("요약 방식", ["핵심 요약", "상세 정리"], horizontal=True)
        generate = st.form_submit_button("요약 만들기", type="primary")
    if generate:
        st.session_state.pop("summary_result", None)
        try:
            source_url = video_url(url) if url.strip() else ""
            if info and source_url != info["url"]:
                raise ValueError("영상 주소가 바뀌었습니다. 새 영상의 자막을 가져온 뒤 요약해 주세요.")
            model = model.strip() or (os.environ.get("OLLAMA_MODEL", "qwen3.5:9b") if provider == "Ollama"
                                      else os.environ.get("GEMINI_MODEL", ""))
            if not model:
                raise ValueError("Gemini에서 사용 가능한 모델 이름을 입력해 주세요.")
            with st.spinner("요약 중…"):
                progress = st.empty()
                body = summarize(transcript, model, provider=provider,
                                 key=(api_key or os.environ.get("GEMINI_API_KEY", "")).strip(), language=language,
                                 detailed=style == "상세 정리",
                                 progress=lambda i, n: progress.caption(f"자막 구간 {i} / {n} 처리 중"))
                progress.empty()
            st.session_state["summary_result"] = dict(summary=body, transcript=transcript, model=model,
                                                       provider=provider, url=source_url, title=info.get("title", ""))
        except Exception as error:
            st.error(plain_error(error))
    if result := st.session_state.get("summary_result"):
        st.divider()
        st.subheader("요약 결과")
        st.caption(f'{result["title"] or "직접 입력한 자막"} · {result["provider"]} / {result["model"]}')
        st.markdown(result["summary"])
        st.download_button("요약 Markdown 다운로드", result["summary"], "youtube-summary.md", mime="text/markdown")
        with st.form("save_archive"):
            title = st.text_input("아카이브 제목", value=result["title"] or "YouTube 요약")
            include = st.checkbox("원본 자막도 함께 보관", value=True)
            if st.form_submit_button("아카이브에 저장"):
                try:
                    path = archive_summary(**{**result, "title": title}, include_transcript=include)
                    st.success(f"저장했습니다: {path.name}")
                except (OSError, ValueError) as error:
                    st.error(plain_error(error))

with download_tab:
    st.subheader("영상 다운로드")
    st.caption("다운로드할 권한이 있는 영상에 사용하세요.")
    with st.form("video_download"):
        link = st.text_input("YouTube 영상 URL", key="download_url")
        mode = st.selectbox("형식", ["MP4 (최대 1080p)", "단일 스트림", "MP3 오디오"])
        submit = st.form_submit_button("PC에 저장", type="primary")
    if submit:
        try:
            progress = st.progress(0, text="다운로드 준비 중…")

            def update(event):
                total = event.get("total_bytes") or event.get("total_bytes_estimate")
                if event.get("status") == "downloading" and total:
                    progress.progress(min(1, event.get("downloaded_bytes", 0) / total), text="다운로드 중…")
                elif event.get("status") == "finished":
                    progress.progress(1.0, text="파일 정리 중…")

            path = download_video(link, mode, progress=update)
            progress.empty()
            st.success(f"다운로드 완료: {path.name}")
            st.code(str(path), language=None)
        except Exception as error:
            st.error(plain_error(error))
    st.caption(f"저장 위치: {DOWNLOADS}")

with archive_tab:
    st.subheader("요약 아카이브")
    st.caption(f"저장 위치: {ARCHIVES}")
    items = archive_items()
    if not items:
        st.info("아직 저장된 요약이 없습니다. 요약 탭에서 아카이브에 저장해 보세요.")
    else:
        query = st.text_input("아카이브 제목 검색").strip().casefold()
        choices = [path for path in items if query in path.stem.casefold()]
        if choices:
            path = st.selectbox("저장된 요약", choices, format_func=lambda path: path.stem)
            try:
                content = path.read_text(encoding="utf-8")
                st.markdown(content)
                st.download_button("아카이브 Markdown 다운로드", content, path.name, mime="text/markdown")
            except (OSError, UnicodeError):
                st.error("파일을 읽지 못했습니다. Markdown 파일의 위치와 UTF-8 인코딩을 확인해 주세요.")
        else:
            st.info("검색 결과가 없습니다.")
