from typing import Any

INPUT_CLASSES = (
    "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "text-slate-900 shadow-sm placeholder:text-slate-400 outline-none transition "
    "focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
)


class StyledFormMixin:
    """Adds Tailwind classes to every widget so templates stay clean."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[call-arg]
        for field in self.fields.values():  # type: ignore[attr-defined]
            field.widget.attrs.setdefault("class", INPUT_CLASSES)
