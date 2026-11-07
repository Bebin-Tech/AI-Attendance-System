# ADR 0002: Defer ML installation until compatibility and licence gates

Status: accepted (selection pending). Date: 2026-11-06.

No ML library, pretrained weight, or biometric API is installed in Phase 1. The preferred candidate remains OpenCV Zoo YuNet/SFace behind a FaceEngine interface, with ONNX Runtime as required by the final architecture. Before adoption, verify exact Python 3.13 wheels and each weight's licence/checksum against primary sources. Do not infer weight licensing from library licensing. If unavailable or unsuitable, document the blocker and propose a maintained alternative without silently substituting.

Phase 5 establishes consent/encryption. Phase 6 selects and evaluates models on representative consented data, including spoof tests. No recognition, liveness, accuracy or privacy-compliance claims can be made from this foundation.
