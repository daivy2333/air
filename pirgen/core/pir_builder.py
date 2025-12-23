# core/pir_builder.py
from .project_model import ProjectModel

class PIRBuilder:
    def __init__(self, model: ProjectModel):
        self.model = model

    def build(self) -> str:
        sections = [
            "<pir>",
            self._build_meta(),
            self._build_units(),
            self._build_dependencies(),
            self._build_symbols(),
            self._build_layout(),
            self._build_snippets(),
            "</pir>"
        ]
        return "\n".join(filter(None, sections))

    def _build_meta(self) -> str:
        langs = ",".join(sorted(self.model.langs))
        return (
            "<meta>\n"
            f"name: {self.model.name}\n"
            f"root: {self.model.root}\n"
            f"profile: {self.model.profile}\n"
            f"lang: {langs}\n"
            "</meta>"
        )

    def _build_units(self) -> str:
        lines = ["<units>"]
        for u in self.model.units:
            lines.append(f"{u.uid}: {u.path} type={u.lang} role={u.role} module={u.module}")
        lines.append("</units>")
        return "\n".join(lines)

    def _build_dependencies(self) -> str:
        if not self.model.dependencies:
            return ""
        lines = ["<dependencies>"]
        for d in self.model.dependencies:
            lines.append(f"{d.src_uid}->{d.verb}:{d.target}")
        lines.append("</dependencies>")
        return "\n".join(lines)

    def _build_symbols(self) -> str:
        if not self.model.symbols:
            return ""
        lines = ["<symbols>"]
        for s in self.model.symbols:
            attr_str = " " + ", ".join([f"{k}={v}" for k, v in s.attrs.items()]) if s.attrs else ""
            lines.append(f"{s.name}:{s.unit_uid} {s.kind}{attr_str}")
        lines.append("</symbols>")
        return "\n".join(lines)

    def _build_layout(self) -> str:
        if not self.model.layout_lines:
            return ""
        lines = ["<layout>"] + self.model.layout_lines + ["</layout>"]
        return "\n".join(lines)

    def _build_snippets(self) -> str:
        if not self.model.snippets:
            return ""
        lines = ["<code-snippets>"]
        for uid, content in self.model.snippets:
            lines.append(f'<snippet unit="{uid}">')
            lines.append("<![CDATA[")
            lines.append(content.strip())
            lines.append("]]>")
            lines.append("</snippet>")
        lines.append("</code-snippets>")
        return "\n".join(lines)