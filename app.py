"""
AI-Based Emergency Ambulance Dispatch & Hospital Optimization System
Main Streamlit Application

CS 2005 - Artificial Intelligence Project
Uses A* Search for ambulance routing and CSP for hospital selection.
"""

import streamlit as st
import random
import copy

from data.city_data import (
    create_city_graph, create_hospitals, create_ambulances,
    randomize_traffic, get_emergency_scenarios
)
from algorithms.astar import astar_search
from algorithms.csp import hospital_csp
from visualization.graph_viz import (
    draw_city_graph, draw_astar_exploration
)
from visualization.csp_viz import (
    draw_csp_domain_reduction, draw_csp_backtracking,
    draw_csp_constraints, draw_csp_assignment
)

# ─── Page Configuration ───
st.set_page_config(
    page_title="AI Emergency Dispatch System",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Initialize Session State ───
if 'city_graph' not in st.session_state:
    st.session_state.city_graph = create_city_graph()
if 'hospitals' not in st.session_state:
    st.session_state.hospitals = create_hospitals()
if 'ambulances' not in st.session_state:
    st.session_state.ambulances = create_ambulances()
if 'dispatch_result' not in st.session_state:
    st.session_state.dispatch_result = None


def main():
    """Main application entry point."""

    # ─── Sidebar Navigation ───
    st.sidebar.title("🚑 AI Dispatch System")
    st.sidebar.markdown("---")

    tab = st.sidebar.radio(
        "Navigation",
        [
            "🆘 Emergency Dispatch",
            "🏥 Hospital Management",
            "⚙️ System Administration",
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**CS 2005 – Artificial Intelligence**\n\n"
        "AI-Based Emergency Ambulance\n"
        "Dispatch & Hospital Optimization"
    )

    # ─── Route to selected tab ───
    if tab == "🆘 Emergency Dispatch":
        emergency_dispatch_tab()
    elif tab == "🏥 Hospital Management":
        hospital_management_tab()
    elif tab == "⚙️ System Administration":
        system_admin_tab()


# ═══════════════════════════════════════════
# TAB 1: EMERGENCY DISPATCH
# ═══════════════════════════════════════════
def emergency_dispatch_tab():
    """Emergency Control Operator interface."""
    st.title("🆘 Emergency Dispatch")
    st.markdown("*Input emergency details to dispatch the nearest ambulance and select optimal hospital.*")

    city = st.session_state.city_graph
    hospitals = st.session_state.hospitals
    ambulances = st.session_state.ambulances

    # ─── Show City Map ───
    st.subheader("City Map Overview")
    fig_map = draw_city_graph(city, hospitals, ambulances, title="City Road Network")
    st.pyplot(fig_map)

    st.markdown("---")

    # ─── Emergency Input Form ───
    st.subheader("📋 Emergency Request")
    col1, col2, col3 = st.columns(3)

    with col1:
        nodes = city.get_nodes()
        emergency_location = st.selectbox("Emergency Location (Node)", nodes, index=16)

    with col2:
        severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])

    with col3:
        icu_required = st.checkbox("ICU Required", value=(severity == "Critical"))

    # Quick scenario loader
    st.markdown("**Or load a scenario:**")
    scenarios = get_emergency_scenarios()
    scenario_names = ["-- Select --"] + [s['name'] for s in scenarios]
    selected_scenario = st.selectbox("Pre-defined Scenarios", scenario_names)

    if selected_scenario != "-- Select --":
        sc = next(s for s in scenarios if s['name'] == selected_scenario)
        emergency_location = sc['location']
        severity = sc['severity']
        icu_required = sc['icu_required']
        st.info(f"Loaded: {sc['name']} | Location: {sc['location']} | Severity: {sc['severity']} | ICU: {sc['icu_required']}")

    st.markdown("---")

    # ─── Dispatch Button ───
    if st.button("🚨 DISPATCH AMBULANCE", type="primary", use_container_width=True):
        run_dispatch(emergency_location, severity, icu_required)


def run_dispatch(emergency_location, severity, icu_required):
    """Run the full dispatch process: A* + CSP."""
    city = st.session_state.city_graph
    hospitals = st.session_state.hospitals
    ambulances = st.session_state.ambulances

    st.markdown("---")
    st.header("📡 Dispatch Results")

    # ─── Step 1: Select nearest available ambulance ───
    st.subheader("Step 1: Select Nearest Ambulance (A* Search)")

    available = [a for a in ambulances if a.is_available]
    if not available:
        st.error("No ambulances available!")
        return

    best_ambulance = None
    best_result = None
    best_cost = float('inf')

    progress = st.progress(0)
    for i, amb in enumerate(available):
        result = astar_search(city, amb.current_node, emergency_location)
        if result and result['cost'] < best_cost:
            best_cost = result['cost']
            best_ambulance = amb
            best_result = result
        progress.progress((i + 1) / len(available))

    if not best_ambulance:
        st.error("No path found to emergency location!")
        return

    st.success(f"**Selected Ambulance:** {best_ambulance.ambulance_id} at node {best_ambulance.current_node} (cost: {best_cost:.2f})")

    # Show A* exploration visualization
    fig_astar = draw_astar_exploration(
        city, best_result, hospitals, ambulances,
        emergency_node=emergency_location,
        ambulance_node=best_ambulance.current_node
    )
    st.pyplot(fig_astar)

    # Show A* steps table
    with st.expander("📋 A* Search Steps Detail"):
        for step in best_result['steps']:
            icon = "🔍" if step['action'] == 'expand' else "🎯"
            st.text(f"{icon} Node {step['current_node']}: g={step['g_score']:.2f}, "
                    f"h={step['h_score']:.2f}, f={step['f_score']:.2f}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Nodes Expanded", best_result['nodes_expanded'])
    col2.metric("Path Cost", f"{best_result['cost']:.2f}")
    col3.metric("Path", " → ".join(best_result['path']))

    st.markdown("---")

    # ─── Step 2: Select hospital using CSP ───
    st.subheader("Step 2: Select Hospital (CSP)")

    csp_result = hospital_csp(hospitals, icu_required, emergency_location, city)

    if csp_result['assigned_hospital']:
        assigned = csp_result['assigned_hospital']
        st.success(f"**Assigned Hospital:** {assigned.name} at node {assigned.node}")

        # Show path from emergency to hospital
        hospital_path_result = astar_search(city, emergency_location, assigned.node)
        if hospital_path_result:
            st.markdown("**Route: Emergency → Hospital**")
            fig_hosp = draw_astar_exploration(
                city, hospital_path_result, hospitals, ambulances,
                emergency_node=emergency_location,
                ambulance_node=best_ambulance.current_node
            )
            st.pyplot(fig_hosp)

            total_cost = best_result['cost'] + hospital_path_result['cost']
            st.info(f"**Total Response Time Cost:** {total_cost:.2f} "
                    f"(Ambulance→Emergency: {best_result['cost']:.2f} + "
                    f"Emergency→Hospital: {hospital_path_result['cost']:.2f})")
    else:
        st.error("No suitable hospital found! All constraints failed.")

    # CSP Visualizations
    st.markdown("#### CSP Constraint Analysis")
    fig_constraints = draw_csp_constraints(csp_result)
    st.pyplot(fig_constraints)

    st.markdown("#### CSP Domain Reduction")
    fig_domain = draw_csp_domain_reduction(csp_result)
    st.pyplot(fig_domain)

    st.markdown("#### CSP Backtracking Steps")
    fig_bt = draw_csp_backtracking(csp_result)
    st.pyplot(fig_bt)

    st.markdown("#### CSP Final Assignment")
    fig_assign = draw_csp_assignment(csp_result, hospitals)
    st.pyplot(fig_assign)

    # Store result
    st.session_state.dispatch_result = {
        'ambulance': best_ambulance,
        'astar_result': best_result,
        'csp_result': csp_result,
    }


# ═══════════════════════════════════════════
# TAB 2: HOSPITAL MANAGEMENT
# ═══════════════════════════════════════════
def hospital_management_tab():
    """Hospital Administrator interface."""
    st.title("🏥 Hospital Management")
    st.markdown("*Update hospital capacity and monitor patient allocation.*")

    hospitals = st.session_state.hospitals

    # ─── Hospital Capacity Dashboard ───
    st.subheader("Hospital Capacity Dashboard")

    cols_per_row = 3
    for i in range(0, len(hospitals), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(hospitals):
                h = hospitals[i + j]
                with cols[j]:
                    with st.container(border=True):
                        occupancy = ((h.total_beds - h.available_beds) / h.total_beds) * 100
                        color = "🟢" if occupancy < 60 else ("🟡" if occupancy < 85 else "🔴")
                        st.markdown(f"#### {color} {h.name}")
                        st.metric("Available Beds", f"{h.available_beds}/{h.total_beds}")
                        st.metric("Doctors", h.doctors_available)
                        st.metric("ICU", "✅ Yes" if h.icu_available else "❌ No")
                        st.progress(1.0 - (h.available_beds / h.total_beds), text=f"Occupancy: {occupancy:.1f}%")

    st.markdown("---")

    # ─── Update Hospital Capacity ───
    st.subheader("Update Hospital Capacity")

    hospital_names = [h.name for h in hospitals]
    selected = st.selectbox("Select Hospital", hospital_names)
    h_idx = hospital_names.index(selected)
    h = hospitals[h_idx]

    col1, col2, col3 = st.columns(3)
    with col1:
        new_beds = st.number_input("Available Beds", 0, h.total_beds, h.available_beds)
    with col2:
        new_doctors = st.number_input("Available Doctors", 0, 20, h.doctors_available)
    with col3:
        new_icu = st.checkbox("ICU Available", h.icu_available)

    if st.button("💾 Update Hospital", type="primary"):
        h.available_beds = new_beds
        h.doctors_available = new_doctors
        h.icu_available = new_icu
        st.success(f"Updated {h.name} successfully!")
        st.rerun()


# ═══════════════════════════════════════════
# TAB 3: SYSTEM ADMINISTRATION
# ═══════════════════════════════════════════
def system_admin_tab():
    """System Administrator interface."""
    st.title("⚙️ System Administration")
    st.markdown("*Manage dataset and traffic conditions.*")

    city = st.session_state.city_graph

    # ─── City Graph ───
    st.subheader("City Graph")
    hospitals = st.session_state.hospitals
    ambulances = st.session_state.ambulances
    fig = draw_city_graph(city, hospitals, ambulances, title="City Road Network with Traffic")
    st.pyplot(fig)

    st.markdown("---")

    # ─── Traffic Management ───
    st.subheader("🚦 Traffic Management")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔀 Randomize All Traffic", type="primary"):
            randomize_traffic(city)
            st.success("Traffic conditions randomized!")
            st.rerun()

    with col2:
        if st.button("🔄 Reset All Traffic (Clear Roads)"):
            for u, v, data in city.get_edges():
                city.update_traffic(u, v, 1.0)
            st.success("All traffic reset to clear!")
            st.rerun()

    # Manual traffic updates
    st.markdown("**Update Individual Road Traffic:**")
    edges = [(u, v) for u, v, _ in city.get_edges()]
    edge_labels = [f"{u} ↔ {v}" for u, v in edges]

    selected_edge = st.selectbox("Select Road", edge_labels)
    if selected_edge:
        idx = edge_labels.index(selected_edge)
        u, v = edges[idx]
        current_tf = city.graph[u][v]['traffic_factor']
        new_tf = st.slider(f"Traffic Factor ({u} ↔ {v})", 1.0, 3.0, current_tf, 0.1)
        if st.button("Update Traffic"):
            city.update_traffic(u, v, new_tf)
            st.success(f"Updated traffic on {u} ↔ {v} to {new_tf}x")
            st.rerun()






if __name__ == "__main__":
    main()
