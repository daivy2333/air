# core/pir_builder.py
from io import StringIO
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

        # Use StringIO for better string concatenation performance
        output = StringIO()
        output.write("<pir>\n")

        meta = self._build_meta()
        if meta:
            output.write(meta)
            output.write("\n")

        units = self._build_units()
        if units:
            output.write(units)
            output.write("\n")

        dep_pool = self._build_dependency_pool()
        if dep_pool:
            output.write(dep_pool)
            output.write("\n")

        deps = self._build_dependencies()
        if deps:
            output.write(deps)
            output.write("\n")

        symbols = self._build_symbols()
        if symbols:
            output.write(symbols)
            output.write("\n")

        profiles = self._build_profiles()
        if profiles:
            output.write(profiles)
            output.write("\n")

        layout = self._build_layout()
        if layout:
            output.write(layout)
            output.write("\n")

        snippets = self._build_snippets()
        if snippets:
            output.write(snippets)
            output.write("\n")

        output.write("</pir>")
        return output.getvalue()

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
    # Profiles (v0.4 extension)
    # -------------------------
    def _build_profiles(self) -> str:
        if not self.model.profiles:
            return ""

        lines = ["<profiles>"]

        # Active profile
        if self.model.active_profile:
            lines.append(f"  active: {self.model.active_profile}")

        # Profile definitions
        for profile_name, profile_data in sorted(self.model.profiles.items()):
            confidence = profile_data.get("confidence", 0.0)
            tags = profile_data.get("tags", [])
            signals = profile_data.get("signals", [])

            lines.append(f"  {profile_name}:")
            lines.append(f"    confidence: {confidence}")

            if tags:
                lines.append("    tags:")
                for tag in sorted(tags):
                    lines.append(f"      - {tag}")

            if signals:
                lines.append("    signals:")
                for signal in sorted(signals):
                    lines.append(f"      - {signal}")

        lines.append("</profiles>")
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
