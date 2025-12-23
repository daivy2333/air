# core/pir_builder.py
from .project_model import ProjectModel


class PIRBuilder:
    def __init__(self, model: ProjectModel):
        self.model = model

    def build(self) -> str:
        # ❗ Builder 不再偷偷改 model
        if not self.model.deps_finalized:
            raise RuntimeError(
                "Dependencies not finalized. Call model.finalize_dependencies() first."
            )

        sections = [
            "<pir>",
            self._build_meta(),
            self._build_units(),
            self._build_dependency_pool(),
            self._build_dependencies(),
            self._build_symbols(),
            self._build_layout(),
            self._build_snippets(),
            "</pir>",
        ]
        return "\n".join(s for s in sections if s)

    # -------------------------
    # Meta
    # -------------------------
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

    # -------------------------
    # Units
    # -------------------------
    def _build_units(self) -> str:
        lines = ["<units>"]
        for u in self.model.units:
            lines.append(
                f"{u.uid}: {u.path} "
                f"type={u.lang} role={u.role} module={u.module}"
            )
        lines.append("</units>")
        return "\n".join(lines)

    # -------------------------
    # Dependency Pool
    # -------------------------
    def _build_dependency_pool(self) -> str:
        if not self.model.dep_pool_items:
            return ""
        lines = ["<dependency-pool>"]
        for did, verb, target in self.model.dep_pool_items:
            lines.append(f"{did}: {verb}:{target}")
        lines.append("</dependency-pool>")
        return "\n".join(lines)

    # -------------------------
    # Dependency Refs
    # -------------------------
    def _build_dependencies(self) -> str:
        if not self.model.dep_refs:
            return ""
        lines = ["<dependencies>"]

        # u0, u1, u2 顺序稳定
        for uid in sorted(self.model.dep_refs, key=lambda x: int(x[1:])):
            refs = self.model.dep_refs[uid]
            if refs:
                lines.append(f"{uid}->refs:[{' '.join(refs)}]")

        lines.append("</dependencies>")
        return "\n".join(lines)

    # -------------------------
    # Symbols
    # -------------------------
    def _build_symbols(self) -> str:
        if not self.model.symbols:
            return ""
        lines = ["<symbols>"]

        for s in self.model.symbols:
            attrs = (
                " " + ", ".join(f"{k}={v}" for k, v in sorted(s.attrs.items()))
                if s.attrs else ""
            )
            lines.append(f"{s.name}:{s.unit_uid} {s.kind}{attrs}")

        lines.append("</symbols>")
        return "\n".join(lines)

    # -------------------------
    # Layout
    # -------------------------
    def _build_layout(self) -> str:
        if not self.model.layout_lines:
            return ""
        return "\n".join(["<layout>", *self.model.layout_lines, "</layout>"])

    # -------------------------
    # Code Snippets
    # -------------------------
    def _build_snippets(self) -> str:
        if not self.model.snippets:
            return ""
        lines = ["<code-snippets>"]
        for uid, content in self.model.snippets:
            lines.extend([
                f'<snippet unit="{uid}">',
                "<![CDATA[",
                content.strip(),
                "]]>",
                "</snippet>",
            ])
        lines.append("</code-snippets>")
        return "\n".join(lines)
