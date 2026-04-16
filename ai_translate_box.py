#!/usr/bin/env python3
"""Floating live AI translation box (English -> Arabic)."""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from openai import OpenAI

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEBOUNCE_MS = 650


class TranslatorBoxApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AI Live Caption: English → Arabic")
        self.root.geometry("560x440")
        self.root.minsize(380, 300)

        self.client: OpenAI | None = None
        self._init_client()

        self.status_var = tk.StringVar(value="جاهز للترجمة المباشرة")
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)

        self.pending_job: str | None = None
        self.request_counter = 0
        self.latest_rendered_request = 0

        self._build_ui()

    def _init_client(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.client = None
            return
        self.client = OpenAI(api_key=api_key)

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        top_row = tk.Frame(frame)
        top_row.pack(fill="x", pady=(0, 8))

        tk.Label(top_row, text="Model:").pack(side="left")
        model_entry = tk.Entry(top_row, textvariable=self.model_var)
        model_entry.pack(side="left", fill="x", expand=True, padx=6)

        refresh_btn = tk.Button(
            top_row,
            text="ترجمة الآن",
            command=self.translate_now,
            bg="#1E88E5",
            fg="white",
            activebackground="#1565C0",
            relief="flat",
            padx=12,
            pady=4,
        )
        refresh_btn.pack(side="right")
        self.refresh_btn = refresh_btn

        tk.Label(frame, text="مربع النص الإنجليزي (Live Input):", anchor="w").pack(fill="x")
        self.input_text = scrolledtext.ScrolledText(frame, wrap="word", height=8)
        self.input_text.pack(fill="both", expand=True, pady=(4, 10))

        tk.Label(frame, text="مربع الترجمة العربي (Live Output):", anchor="w").pack(fill="x")
        self.output_text = scrolledtext.ScrolledText(frame, wrap="word", height=8)
        self.output_text.pack(fill="both", expand=True, pady=(4, 10))

        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padx=8,
            pady=4,
        )
        status_bar.pack(fill="x", side="bottom")

        self.input_text.bind("<KeyRelease>", self._on_input_changed)
        self.root.bind("<Control-Return>", lambda _event: self.translate_now())

    def _on_input_changed(self, _event: tk.Event[tk.Misc]) -> None:
        if self.pending_job is not None:
            self.root.after_cancel(self.pending_job)

        self.pending_job = self.root.after(DEBOUNCE_MS, self.translate_now)
        self.status_var.set("جاري التحضير للترجمة...")

    def translate_now(self) -> None:
        if self.pending_job is not None:
            self.root.after_cancel(self.pending_job)
            self.pending_job = None

        source = self.input_text.get("1.0", tk.END).strip()
        if not source:
            self._set_output("")
            self.status_var.set("اكتب نص إنجليزي في المربع الأول")
            return

        if self.client is None:
            messagebox.showerror(
                "OPENAI_API_KEY غير موجود",
                "حط متغير البيئة OPENAI_API_KEY وشغّل التطبيق مرة ثانية.",
            )
            self.status_var.set("لا يمكن الترجمة بدون API key")
            return

        self.request_counter += 1
        request_id = self.request_counter
        self.set_busy(True, "جاري الترجمة المباشرة...")
        thread = threading.Thread(target=self._translate_worker, args=(source, request_id), daemon=True)
        thread.start()

    def _translate_worker(self, source: str, request_id: int) -> None:
        assert self.client is not None
        try:
            response = self.client.responses.create(
                model=self.model_var.get().strip() or DEFAULT_MODEL,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a live caption translator. Translate English into natural Arabic. "
                            "Output Arabic translation only, no explanation."
                        ),
                    },
                    {"role": "user", "content": source},
                ],
                temperature=0.2,
                max_output_tokens=700,
            )
            translated = (response.output_text or "").strip() or "(لم يتم توليد ترجمة)"
            self.root.after(0, self._apply_translation, request_id, translated)
        except Exception as exc:  # noqa: BLE001
            self.root.after(0, self._handle_error, str(exc))

    def _apply_translation(self, request_id: int, translated: str) -> None:
        if request_id < self.latest_rendered_request:
            return

        self.latest_rendered_request = request_id
        self._set_output(translated)
        self.set_busy(False, "تم تحديث الترجمة ✔")

    def _handle_error(self, error_msg: str) -> None:
        self.set_busy(False, "حصل خطأ")
        messagebox.showerror("Translation Error", error_msg)

    def _set_output(self, value: str) -> None:
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", value)

    def set_busy(self, is_busy: bool, status: str) -> None:
        self.refresh_btn.configure(state="disabled" if is_busy else "normal")
        self.status_var.set(status)


def main() -> None:
    root = tk.Tk()
    app = TranslatorBoxApp(root)
    app.input_text.insert(
        "1.0",
        "This text will be translated to Arabic automatically while you type.",
    )
    app.translate_now()
    root.mainloop()


if __name__ == "__main__":
    main()
