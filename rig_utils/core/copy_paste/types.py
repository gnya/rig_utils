from typing import Any, Literal

CopyBoneSpace = Literal["WORLD", "POSE", "LOCAL_WITH_PARENT", "LOCAL"]
CopyBoneMatrix = list[list[float]]
CopyBoneProps = dict[str, Any]
CopyBoneData = dict[str, dict[str, CopyBoneMatrix | CopyBoneProps]]
