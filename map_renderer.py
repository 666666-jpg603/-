# utils/map_renderer.py
import folium
from streamlit_folium import st_folium
import json

def render_map_with_markers(start_point, end_point, obstacles=None, zoom=16):
    """
    渲染带起点、终点和障碍物的地图
    :param start_point: [lng, lat] GCJ02
    :param end_point: [lng, lat] GCJ02
    :param obstacles: list of polygons [[[lng,lat], ...], ...]
    """
    m = folium.Map(location=[start_point[1], start_point[0]], zoom_start=zoom)

    # 添加起点
    folium.Marker(
        location=[start_point[1], start_point[0]],
        popup='起点A',
        icon=folium.Icon(color='green')
    ).add_to(m)

    # 添加终点
    folium.Marker(
        location=[end_point[1], end_point[0]],
        popup='终点B',
        icon=folium.Icon(color='red')
    ).add_to(m)

    # 添加障碍物（多边形）
    if obstacles:
        for i, poly in enumerate(obstacles):
            folium.Polygon(
                locations=[[p[1], p[0]] for p in poly],  # Folium uses [lat, lng]
                color='blue',
                weight=2,
                fill=True,
                fill_color='blue',
                fill_opacity=0.3,
                tooltip=f'障碍物{i+1}'
            ).add_to(m)

    return m

def save_obstacles_to_json(obstacles, filename="obstacle_config.json"):
    """保存障碍物到JSON文件"""
    data = {
        "version": "v12.2",
        "obstacles": obstacles,
        "save_time": "2026-03-31 11:07:05"  # 可根据实际时间动态生成
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_obstacles_from_json(filename="obstacle_config.json"):
    """从JSON加载障碍物"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("obstacles", [])
    except FileNotFoundError:
        return []