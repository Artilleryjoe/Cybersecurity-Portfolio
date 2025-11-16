#!/usr/bin/env python3
"""Mobile Security Analysis Tool
Automates chained analysis tasks for Android APKs and iOS IPAs."""

from __future__ import annotations

import argparse
import json
import plistlib
import shutil
import subprocess
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional
from xml.etree import ElementTree as ET
from zipfile import ZipFile


@dataclass
class AnalysisContext:
    """Holds shared state between chained analysis tasks."""

    target_path: Path
    output_dir: Path
    data: Dict[str, object] = field(default_factory=dict)
    findings: List["Finding"] = field(default_factory=list)


@dataclass
class Finding:
    """Represents a structured finding with taxonomy metadata."""

    identifier: str
    title: str
    description: str
    taxonomy: List[str]
    severity: str
    references: List[str] = field(default_factory=list)


def record_finding(context: AnalysisContext, finding: Finding) -> None:
    """Add a structured finding to the analysis context."""

    context.findings.append(finding)


@dataclass
class AnalysisTask:
    name: str
    description: str
    runner: Callable[[AnalysisContext, Path], int]


def run_tool(command: List[str], cwd: Optional[Path] = None) -> int:
    """Run an external command and stream its output."""
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Command failed: {' '.join(command)}")
        if result.stderr:
            print(result.stderr)
    else:
        if result.stdout:
            print(result.stdout)
    return result.returncode


def ensure_tool_installed(tool_name: str) -> bool:
    if shutil.which(tool_name) is None:
        print(f"[!] {tool_name} not found. Please install it first.")
        return False
    return True


def save_findings_report(context: AnalysisContext) -> None:
    """Persist taxonomy-aware findings and severity tags to disk."""

    report_path = context.output_dir / "findings_report.json"
    findings_data = [asdict(finding) for finding in context.findings]
    severity_counts: Dict[str, int] = {}
    for finding in context.findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

    report_path.write_text(
        json.dumps(
            {
                "summary": {
                    "total_findings": len(findings_data),
                    "severity_breakdown": severity_counts,
                },
                "findings": findings_data,
            },
            indent=2,
        )
    )
    print(f"[*] Saved findings report to {report_path}")


# --- Android task implementations --------------------------------------------------

def decompile_with_apktool(context: AnalysisContext, task_out: Path) -> int:
    if not ensure_tool_installed("apktool"):
        return 1
    task_out.mkdir(parents=True, exist_ok=True)
    return run_tool(["apktool", "d", "-f", str(context.target_path), "-o", str(task_out)])


def jadx_decompile(context: AnalysisContext, task_out: Path) -> int:
    if not ensure_tool_installed("jadx"):
        return 1
    task_out.mkdir(parents=True, exist_ok=True)
    return run_tool(["jadx", str(context.target_path), "-d", str(task_out)])


def derive_android_package_name(context: AnalysisContext) -> Optional[str]:
    if "android_package" in context.data:
        return context.data["android_package"]  # type: ignore[return-value]

    manifest_path = context.output_dir / "apktool" / "AndroidManifest.xml"
    if not manifest_path.exists():
        return None

    try:
        tree = ET.parse(manifest_path)
        package_name = tree.getroot().attrib.get("package")
    except ET.ParseError:
        package_name = None

    if package_name:
        context.data["android_package"] = package_name
    return package_name


def generate_frida_helper(context: AnalysisContext, task_out: Path) -> int:
    if not ensure_tool_installed("frida"):
        return 1

    task_out.mkdir(parents=True, exist_ok=True)
    package_name = derive_android_package_name(context) or "<replace.with.package>"

    script_content = textwrap.dedent(
        """
        Java.perform(function () {
          var Activity = Java.use('android.app.Activity');
          Activity.onResume.implementation = function () {
            send('Activity resumed: ' + this.getClass().getName());
            return this.onResume();
          };
        });
        """
    ).strip()

    command_snippet = textwrap.dedent(
        f"""
        # Launch the target application with your custom Frida script
        frida -U -f {package_name} -l frida_hook_template.js --no-pause

        # Trace exported functions or Java classes dynamically
        frida-trace -U -i 'java!*' {package_name}
        """
    ).strip()

    (task_out / "frida_hook_template.js").write_text(script_content)
    (task_out / "frida_commands.txt").write_text(command_snippet)

    print("[*] Generated Frida helper artifacts (script template and usage notes)")
    return 0


ANDROID_TASKS: List[AnalysisTask] = [
    AnalysisTask(
        name="apktool",
        description="Decompiling resources with apktool",
        runner=decompile_with_apktool,
    ),
    AnalysisTask(
        name="jadx",
        description="Generating Java sources with JADX",
        runner=jadx_decompile,
    ),
    AnalysisTask(
        name="frida_helper",
        description="Generating Frida instrumentation helpers",
        runner=generate_frida_helper,
    ),
]


# --- iOS task helpers --------------------------------------------------------------

def _find_ios_app_dir(extract_dir: Path) -> Optional[Path]:
    payload_dir = extract_dir / "Payload"
    if not payload_dir.exists():
        return None
    apps = sorted(payload_dir.glob("*.app"))
    return apps[0] if apps else None


def _load_info_plist(context: AnalysisContext) -> Optional[dict]:
    if "ios_info_plist" in context.data:
        return context.data["ios_info_plist"]  # type: ignore[return-value]

    app_dir = context.data.get("ios_app_dir")
    if not isinstance(app_dir, Path):
        print("[!] Unable to locate Payload/*.app directory. Extract step may have failed.")
        return None

    plist_path = app_dir / "Info.plist"
    if not plist_path.exists():
        print("[!] Info.plist not found in extracted app bundle.")
        return None

    with plist_path.open("rb") as plist_file:
        info = plistlib.load(plist_file)

    context.data["ios_info_plist"] = info
    return info


# --- iOS task implementations ------------------------------------------------------

def extract_ios_payload(context: AnalysisContext, task_out: Path) -> int:
    task_out.mkdir(parents=True, exist_ok=True)
    try:
        with ZipFile(context.target_path) as ipa:
            ipa.extractall(task_out)
    except Exception as exc:  # pragma: no cover - informative logging
        print(f"[!] Failed to extract IPA: {exc}")
        return 1

    app_dir = _find_ios_app_dir(task_out)
    if app_dir:
        context.data["ios_app_dir"] = app_dir
        print(f"[*] Located iOS app bundle: {app_dir}")
    else:
        print("[!] Could not locate Payload/*.app after extraction.")
        return 1

    return 0


def summarize_ios_metadata(context: AnalysisContext, task_out: Path) -> int:
    info = _load_info_plist(context)
    if info is None:
        return 1

    summary = {
        "bundle_identifier": info.get("CFBundleIdentifier"),
        "bundle_version": info.get("CFBundleShortVersionString"),
        "minimum_os_version": info.get("MinimumOSVersion"),
        "supports_iPad": info.get("UISupportedInterfaceOrientations~ipad") is not None,
        "ats_configuration": info.get("NSAppTransportSecurity", {}),
    }

    task_out.mkdir(parents=True, exist_ok=True)
    summary_path = task_out / "info_plist_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"[*] Saved Info.plist summary to {summary_path}")
    return 0


def enumerate_ios_url_schemes(context: AnalysisContext, task_out: Path) -> int:
    info = _load_info_plist(context)
    if info is None:
        return 1

    url_types = info.get("CFBundleURLTypes", []) or []
    schemes: List[str] = []
    for entry in url_types:
        entry_schemes = entry.get("CFBundleURLSchemes") or []
        schemes.extend(entry_schemes)

    task_out.mkdir(parents=True, exist_ok=True)
    output_path = task_out / "url_schemes.txt"
    if schemes:
        output_path.write_text("\n".join(schemes))
        print(f"[*] Enumerated URL schemes: {', '.join(schemes)}")
        record_finding(
            context,
            Finding(
                identifier="ios.url_schemes",
                title="Custom URL schemes exposed",
                description=(
                    "The application declares custom URL schemes which could be used"
                    " for inter-app communication. Review handlers for potential"
                    " injection or abuse."
                ),
                taxonomy=["ios", "url_scheme", "surface"],
                severity="informational",
                references=[
                    "https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app"
                ],
            ),
        )
    else:
        output_path.write_text("<no custom URL schemes declared>")
        print("[*] No custom URL schemes declared in Info.plist")

    return 0


def analyze_ios_transport_security(context: AnalysisContext, task_out: Path) -> int:
    info = _load_info_plist(context)
    if info is None:
        return 1

    ats = info.get("NSAppTransportSecurity", {})
    report = {
        "allows_arbitrary_loads": ats.get("NSAllowsArbitraryLoads", False),
        "allows_http_loads": ats.get("NSAllowsArbitraryLoadsInWebContent", False)
        or ats.get("NSAllowsLocalNetworking", False),
        "exception_domains": list((ats.get("NSExceptionDomains") or {}).keys()),
    }

    task_out.mkdir(parents=True, exist_ok=True)
    report_path = task_out / "ats_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"[*] Saved ATS report to {report_path}")

    if report["allows_arbitrary_loads"]:
        record_finding(
            context,
            Finding(
                identifier="ios.ats.arbitrary_loads",
                title="ATS allows arbitrary loads",
                description=(
                    "NSAppTransportSecurity configuration allows arbitrary network"
                    " loads which weakens transport protections."
                ),
                taxonomy=["ios", "transport_security", "ats"],
                severity="high",
                references=[
                    "https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity"
                ],
            ),
        )

    if report["allows_http_loads"]:
        record_finding(
            context,
            Finding(
                identifier="ios.ats.http_loads",
                title="ATS allows HTTP loads",
                description=(
                    "The ATS policy permits HTTP loads or local networking"
                    " exceptions. Ensure plaintext traffic is justified and"
                    " properly scoped."
                ),
                taxonomy=["ios", "transport_security", "http"],
                severity="medium",
                references=[
                    "https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity"
                ],
            ),
        )

    if report["exception_domains"]:
        record_finding(
            context,
            Finding(
                identifier="ios.ats.exception_domains",
                title="ATS exception domains configured",
                description=(
                    "The ATS policy includes exception domains: "
                    + ", ".join(report["exception_domains"])
                    + ". Review these domains to confirm TLS requirements."
                ),
                taxonomy=["ios", "transport_security", "exceptions"],
                severity="low",
            ),
        )
    return 0


def generate_lldb_helper(context: AnalysisContext, task_out: Path) -> int:
    if not ensure_tool_installed("lldb"):
        return 1

    task_out.mkdir(parents=True, exist_ok=True)
    info = _load_info_plist(context)
    executable = None
    bundle_identifier = None
    if info:
        executable = info.get("CFBundleExecutable")
        bundle_identifier = info.get("CFBundleIdentifier")

    attach_target = executable or bundle_identifier or "<process-name>"

    lldb_commands = textwrap.dedent(
        f"""
        # Launch the target and pause before UIApplicationMain
        process attach --name {attach_target}
        breakpoint set --name UIApplicationMain
        breakpoint command add 1
        > expression -l objc -O -- '[[NSBundle mainBundle] bundleIdentifier]'
        > continue
        DONE

        # Inspect NSURLSession configuration classes
        expr -l objc -O -- [[NSURLSession sharedSession] configuration]
        """
    ).strip()

    tips = textwrap.dedent(
        """
        Use the generated LLDB commands to attach to the running process,
        dump bundle metadata, and inspect networking classes. Combine this helper
        with Frida scripts for runtime method tracing when jailbroken devices are
        available.
        """
    ).strip()

    (task_out / "lldb_commands.txt").write_text(lldb_commands)
    (task_out / "helper_notes.txt").write_text(tips)
    print("[*] Generated LLDB helper commands for dynamic instrumentation")
    return 0


IOS_TASKS: List[AnalysisTask] = [
    AnalysisTask(
        name="ipa_extract",
        description="Extracting IPA contents",
        runner=extract_ios_payload,
    ),
    AnalysisTask(
        name="metadata",
        description="Summarizing Info.plist metadata",
        runner=summarize_ios_metadata,
    ),
    AnalysisTask(
        name="url_schemes",
        description="Enumerating custom URL schemes",
        runner=enumerate_ios_url_schemes,
    ),
    AnalysisTask(
        name="ats_review",
        description="Reviewing App Transport Security configuration",
        runner=analyze_ios_transport_security,
    ),
    AnalysisTask(
        name="lldb_helper",
        description="Generating LLDB instrumentation helpers",
        runner=generate_lldb_helper,
    ),
]


PLATFORM_TASKS = {
    "android": ANDROID_TASKS,
    "ios": IOS_TASKS,
}


def detect_platform(app_path: Path) -> Optional[str]:
    suffix = app_path.suffix.lower()
    if suffix == ".apk":
        return "android"
    if suffix == ".ipa":
        return "ios"
    return None


def run_pipeline(platform: str, context: AnalysisContext) -> None:
    tasks = PLATFORM_TASKS[platform]
    for task in tasks:
        print(f"[*] {task.description} ({task.name})")
        task_output_dir = context.output_dir / task.name
        result = task.runner(context, task_output_dir)
        if result != 0:
            print(f"[!] Task '{task.name}' failed. Review logs before proceeding.")
        else:
            print(f"[+] Task '{task.name}' completed successfully.\n")
    save_findings_report(context)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Static mobile app analysis with chained tasks for Android and iOS",
    )
    parser.add_argument("app", help="Path to the target APK or IPA file")
    parser.add_argument(
        "--out", default="analysis_output", help="Directory to store results"
    )
    parser.add_argument(
        "--platform",
        choices=["auto", "android", "ios"],
        default="auto",
        help="Platform of the target. Defaults to auto-detection based on the file extension.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    target_path = Path(args.app).resolve()
    if not target_path.exists():
        raise SystemExit(f"[!] Target file does not exist: {target_path}")

    if args.platform == "auto":
        platform = detect_platform(target_path)
        if platform is None:
            raise SystemExit("[!] Unable to detect platform. Use --platform to specify explicitly.")
    else:
        platform = args.platform

    context = AnalysisContext(
        target_path=target_path,
        output_dir=Path(args.out).resolve(),
    )
    context.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting {platform} analysis pipeline for {target_path}")
    run_pipeline(platform, context)
    print("[*] Analysis complete.")


if __name__ == "__main__":
    main()
