from openai import OpenAI

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import VoiceMemo
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_MESSAGE = {
    "role": "system",
    "content": """You are helping organize short voice memos. 

                For each memo transcript:
                - Return a concise 4–5 word summary of the main idea or topic.
                - If the memo includes a researchable question or topic, provide a short, informative response. This response should be two to three sentences.
                - If no response is needed, set the value to null (not the string "null").

                Respond in valid JSON with two keys: "summary" and "response".

                Example input:
                User: Why are they called hummingbirds?

                Example output:
                {"summary": "etymology of hummingbirds", "response": "The flapping of their wings produces a humming sound."}
                """,
}


def input_to_memo(transcript):
    # --- 2. Analyze with GPT ---
    messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": f"Transcript: {transcript}"},
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, temperature=0.5
    )

    reply = completion.choices[0].message.content

    # Parse reply
    print("reply!" + reply)

    try:
        data = json.loads(reply)

        summary = data.get("summary", "").strip()
        llm_response = data.get("response")

        # Normalize null string or empty response to None
        if llm_response is None or str(llm_response).lower() == "null":
            llm_response = None

        print("summary: " + summary)
        if llm_response is not None:
            print("llm response: " + llm_response)
        else:
            print("no llm response")

        return (summary, llm_response)

    except json.JSONDecodeError:
        print("Failed to parse LLM reply as JSON:", reply)
        # You could log this, alert yourself, or fall back to your old parsing logic here


def memo_detail_view(request, memo_id):
    memo = get_object_or_404(VoiceMemo, id=memo_id)
    return render(request, "memo_detail.html", {"memo": memo})


def new_memo_text_view(request):
    if request.method == "POST":
        memo = VoiceMemo()
        memo.save()

        transcript = request.POST["text"]

        memo.transcript = transcript
        summary, llm_response = input_to_memo(transcript)
        memo.summary = summary
        memo.llm_response = llm_response
        memo.save()

        return redirect("memo_detail", pk=memo.id)

    return render(request, "upload_text.html")


@csrf_exempt
def upload_view(request):
    if request.method == "POST":
        audio = request.FILES["audio"]
        memo = VoiceMemo(audio_file=audio)
        memo.save()

        # Save file locally for Whisper API
        audio_path = default_storage.save(memo.audio_file.name, audio)
        audio_full_path = default_storage.path(audio_path)

        # --- 1. Transcribe with Whisper ---
        with open(audio_full_path, "rb") as f:
            print("starting transcription")
            try:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", file=f
                )
            except Exception as e:
                # Handle OpenAI quota or API errors gracefully
                print("Transcription failed: " + str(e))
                return render(
                    request, "upload.html", {"error": f"Transcription failed: {str(e)}"}
                )
        transcript = transcription.text
        print("Transcript completed! " + transcript)
        memo.transcript = transcript

        summary, llm_response = input_to_memo(transcript)

        memo.summary = summary
        memo.llm_response = llm_response
        memo.save()

        return redirect("memo_detail", pk=memo.id)

    return render(request, "upload.html")


class MemoListView(ListView):
    model = VoiceMemo
    template_name = "memo_list.html"
    context_object_name = "memos"
    ordering = ["-created_at"]  # Most recent first


class MemoDetailView(DetailView):
    model = VoiceMemo
    template_name = "memo_detail.html"
    context_object_name = "memo"
