"""
Day 70 课后作业 1（基础巩固）：基础巩固：为多模态路由器补充视频（video）模态关键帧抽帧管线
工单：STARMIND-070
"""

def route_video_pipeline(duration_sec: int) -> list[str]:
    if duration_sec <= 60:
        return ["keyframe_extract", "vlm_understand"]
    return ["scene_segment", "keyframe_extract", "map_reduce_summary"]


assert route_video_pipeline(30) == ["keyframe_extract", "vlm_understand"]
assert "map_reduce_summary" in route_video_pipeline(300)
print("视频多模态管线路由通过")

