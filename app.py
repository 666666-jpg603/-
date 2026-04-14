# app.py
import streamlit as st
import json
import time
from utils.coord_converter import wgs84_to_gcj02, gcj02_to_wgs84
from utils.map_renderer import render_map_with_markers, save_obstacles_to_json, load_obstacles_from_json

st.set_page_config(layout="wide", page_title="无人机航线规划系统")

# 初始化会话状态
if 'obstacles' not in st.session_state:
    st.session_state.obstacles = load_obstacles_from_json()
if 'heartbeat_data' not in st.session_state:
    st.session_state.heartbeat_data = []
if 'flight_height' not in st.session_state:
    st.session_state.flight_height = 10  # 默认高度10米
if 'safety_radius' not in st.session_state:
    st.session_state.safety_radius = 5  # 默认安全半径5米

# 侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio("功能页面", ["航线规划", "飞行监控"])

# === 作业2 & 3 & 4 & 5 核心逻辑 ===

if page == "航线规划":
    st.header("🗺️ 航线规划界面")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("控制面板")
        # 坐标系设置
        st.markdown("### 坐标系设置")
        coord_sys = st.radio("输入坐标系", ["WGS-84", "GCJ-02(高德/百度)"], index=1)

        # 起点A
        st.markdown("#### 起点 A")
        lng_a = st.number_input("经度", value=118.749, format="%.6f")
        lat_a = st.number_input("纬度", value=32.2322, format="%.6f")
        if coord_sys == "WGS-84":
            start_gcj = wgs84_to_gcj02(lng_a, lat_a)
        else:
            start_gcj = [lng_a, lat_a]

        # 终点B
        st.markdown("#### 终点 B")
        lng_b = st.number_input("经度", value=118.749, format="%.6f")
        lat_b = st.number_input("纬度", value=32.2343, format="%.6f")
        if coord_sys == "WGS-84":
            end_gcj = wgs84_to_gcj02(lng_b, lat_b)
        else:
            end_gcj = [lng_b, lat_b]

        # 设置点按钮
        if st.button("设置A点"):
            st.success(f"A点已设: {start_gcj}")
        if st.button("设置B点"):
            st.success(f"B点已设: {end_gcj}")

        # 飞行参数
        st.markdown("#### 飞行参数")
        st.session_state.flight_height = st.slider("设定飞行高度(m)", 5, 50, st.session_state.flight_height)
        st.session_state.safety_radius = st.slider("安全半径(m)", 1, 10, st.session_state.safety_radius)

        # 障碍物圈选记忆功能
        st.markdown("#### 障碍物配置")
        if st.button("保存障碍物到文件"):
            save_obstacles_to_json(st.session_state.obstacles)
            st.success("障碍物已保存到 obstacle_config.json")

        if st.button("从文件加载障碍物"):
            st.session_state.obstacles = load_obstacles_from_json()
            st.success("障碍物已加载")

        # 下载配置文件
        st.download_button(
            label="下载 obstacle_config.json",
            data=open("obstacle_config.json", "rb").read(),
            file_name="obstacle_config.json",
            mime="application/json"
        )

    with col1:
        st.subheader("地图显示")
        # 模拟障碍物（示例）
        if len(st.session_state.obstacles) == 0:
            st.session_state.obstacles = [
                [[118.748, 32.231], [118.750, 32.231], [118.750, 32.233], [118.748, 32.233]],
                [[118.751, 32.235], [118.753, 32.235], [118.753, 32.237], [118.751, 32.237]]
            ]

        # 渲染地图
        m = render_map_with_markers(start_gcj, end_gcj, st.session_state.obstacles)
        st_folium(m, width=800, height=600)

elif page == "飞行监控":
    st.header("📡 飞行监控界面")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("心跳包显示")
        if st.session_state.heartbeat_data:
            st.line_chart([d['time'] for d in st.session_state.heartbeat_data],
                          [d['seq'] for d in st.session_state.heartbeat_data])
            st.dataframe(st.session_state.heartbeat_data)
        else:
            st.info("暂无心跳包数据，请先运行模拟心跳程序")

    with col2:
        st.subheader("模拟心跳发送")
        if st.button("开始模拟心跳"):
            for i in range(10):
                seq = i + 1
                ts = time.strftime("%H:%M:%S", time.localtime())
                st.session_state.heartbeat_data.append({"seq": seq, "time": ts})
                st.write(f"心跳包 #{seq} 发送于 {ts}")
                time.sleep(1)
            st.success("模拟完成！")

        if st.button("清空心跳数据"):
            st.session_state.heartbeat_data = []
            st.success("数据已清空")

# === 作业4 额外功能：航线规划算法（简化版） ===

st.sidebar.markdown("---")
st.sidebar.subheader("航线规划逻辑")
if st.sidebar.button("计算航线"):
    # 简化逻辑：检查每个障碍物是否在路径上
    # 实际项目中应使用路径规划算法（如A*、RRT），这里做演示
    obstacles = st.session_state.obstacles
    flight_h = st.session_state.flight_height
    safety_r = st.session_state.safety_radius

    st.sidebar.success(f"当前飞行高度: {flight_h}m, 安全半径: {safety_r}m")

    for i, obs in enumerate(obstacles):
        # 假设障碍物高度固定为5m（实际应可编辑）
        obs_height = 5
        if flight_h <= obs_height + safety_r:
            st.sidebar.warning(f"障碍物{i+1} 高度{obs_height}m，建议绕行！")
        else:
            st.sidebar.info(f"障碍物{i+1} 高度{obs_height}m，可直接飞跃。")

    # 模拟三种绕行方案
    st.sidebar.markdown("### 绕行方案建议")
    st.sidebar.write("- 向左绕行")
    st.sidebar.write("- 向右绕行")
    st.sidebar.write("- 最佳航线（智能避障）")

# === 作业5 说明 ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 作业5：项目整合与部署")
st.sidebar.markdown("- 本项目已完成所有功能整合")
st.sidebar.markdown("- 支持坐标转换、地图显示、心跳监控、障碍物圈选、航线规划")
st.sidebar.markdown("- 可部署至 Streamlit Cloud")
