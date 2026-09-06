from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

payload = {
    "spdxVersion": "SPDX-2.3",
    "dataLicense": "CC0-1.0",
    "SPDXID": "SPDXRef-DOCUMENT",
    "name": "DIKWP-QINGYUAN-OS-1.0.0",
    "documentNamespace": "https://example.org/spdx/dikwp-qingyuan-os/1.0.0",
    "creationInfo": {"created": "2026-09-06T00:00:00Z", "creators": ["Tool: DIKWP-QINGYUAN-OS build_sbom.py"]},
    "packages": [
        {
            "name": "DIKWP-QINGYUAN-OS",
            "SPDXID": "SPDXRef-Package-Qingyuan",
            "versionInfo": "1.0.0",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "AGPL-3.0-or-later",
            "licenseDeclared": "AGPL-3.0-or-later",
            "copyrightText": "Copyright 2026 Yucong Duan and contributors",
            "externalRefs": [],
        }
    ],
    "relationships": [{"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-Package-Qingyuan"}],
    "annotations": [
        {"annotationType": "OTHER", "annotator": "Tool: build_sbom.py", "annotationDate": "2026-09-06T00:00:00Z", "comment": "Runtime dependencies: Python standard library only."}
    ],
}
(ROOT / "SBOM.spdx.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(ROOT / "SBOM.spdx.json")
