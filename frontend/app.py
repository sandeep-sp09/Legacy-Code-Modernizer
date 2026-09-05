"""
Legacy Code Modernizer - Streamlit UI Application

Connects to the FastAPI backend service (http://localhost:8000) to orchestrate:
1. File upload for Pascal/C source.
2. AST parsing & Dependency graph visualization.
3. LLM generation of idiomatic modern C++.
4. Side-by-side diff comparison and code download.
"""

import os
import json
import requests
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

# Page configuration
st.set_page_config(
    page_title="Legacy Code Modernizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom dark-theme styling tweaks
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #8B5CF6, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Configuration")
backend_url = st.sidebar.text_input("FastAPI Backend URL", value="http://localhost:8000")

# Check backend health
backend_online = False
try:
    health_resp = requests.get(f"{backend_url.rstrip('/')}/health", timeout=1.5)
    if health_resp.status_code == 200:
        backend_online = True
        st.sidebar.success("🟢 Backend Connected (:8000)")
except Exception:
    st.sidebar.warning("🟡 Backend Offline (Demo Mode Available)")

# Sample Selector
st.sidebar.subheader("📁 Quick Load Samples")
sample_choice = st.sidebar.radio(
    "Choose a preloaded sample:",
    ("Pascal Sample (sample1.pas)", "C Sample (sample1.c)", "Custom Upload")
)

# Sample Code Content
SAMPLE_PASCAL = """program Sample1;
var
  x, y, sum: integer;

function AddNumbers(a, b: integer): integer;
begin
  AddNumbers := a + b;
end;

begin
  x := 5;
  y := 10;
  sum := AddNumbers(x, y);
  writeln('Sum is: ', sum);
end."""

SAMPLE_C = """#include <stdio.h>

int add_numbers(int a, int b) {
    return a + b;
}

int main() {
    int x = 5, y = 10;
    int sum = add_numbers(x, y);
    printf("Sum is: %d\\n", sum);
    return 0;
}"""

# ---------------------------------------------------------------------------
# Main App Header
# ---------------------------------------------------------------------------
st.markdown('<p class="main-header">Legacy Code Modernizer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Tree-sitter AST &bull; Call Graph Analysis &bull; '
    'Qwen2.5-Coder LLM &bull; Modern C++ Synthesis</p>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Input Section
# ---------------------------------------------------------------------------
source_code = ""
filename = "source.pas"
language = "pascal"

if sample_choice == "Pascal Sample (sample1.pas)":
    source_code = SAMPLE_PASCAL
    filename = "sample1.pas"
    language = "pascal"
elif sample_choice == "C Sample (sample1.c)":
    source_code = SAMPLE_C
    filename = "sample1.c"
    language = "c"
else:
    uploaded_file = st.file_uploader(
        "Upload Pascal or C source file",
        type=["pas", "pp", "dpr", "lpr", "c", "h"]
    )
    if uploaded_file:
        source_code = uploaded_file.read().decode("utf-8", errors="replace")
        filename = uploaded_file.name
        ext = os.path.splitext(filename)[1].lower()
        language = "pascal" if ext in [".pas", ".pp", ".dpr", ".lpr"] else "c"

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"📄 Legacy Source ({filename})")
    edited_code = st.text_area(
        "Edit or verify source code:",
        value=source_code,
        height=320,
        key="source_editor"
    )

    run_pipeline = st.button("🚀 Run Modernization Pipeline", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Pipeline Telemetry")
    t1, t2, t3 = st.columns(3)
    metric_funcs = t1.empty()
    metric_edges = t2.empty()
    metric_status = t3.empty()

    metric_funcs.metric("Functions", "—")
    metric_edges.metric("Call Edges", "—")
    metric_status.metric("Pipeline", "Ready")

    st.info(
        "**Pipeline Stages:**\n"
        "1. Tree-sitter AST parsing\n"
        "2. NetworkX dependency call graph\n"
        "3. IR-grounded prompt construction\n"
        "4. Qwen2.5-Coder LLM synthesis\n"
        "5. C++ syntax & hallucination validation"
    )

# ---------------------------------------------------------------------------
# Pipeline Execution Logic
# ---------------------------------------------------------------------------
if run_pipeline:
    if not edited_code.strip():
        st.error("Please provide valid source code.")
    else:
        with st.spinner("Executing modernization pipeline..."):
            result_data = None

            if backend_online:
                try:
                    # 1. Upload
                    files = {"file": (filename, edited_code.encode("utf-8"))}
                    upload_res = requests.post(f"{backend_url.rstrip('/')}/upload", files=files, timeout=10)
                    upload_res.raise_for_status()
                    file_id = upload_res.json()["file_id"]

                    # 2. Process
                    process_res = requests.post(f"{backend_url.rstrip('/')}/process/{file_id}", timeout=150)
                    process_res.raise_for_status()
                    result_data = process_res.json()
                except Exception as e:
                    st.error(f"Backend processing error: {e}")

            # Fallback to Demo Simulation if backend offline or failed
            if not result_data:
                st.info("Demonstrating offline simulation results:")
                if language == "pascal":
                    demo_cpp = """#include <iostream>

int AddNumbers(int a, int b) {
    return a + b;
}

int main() {
    int x = 5;
    int y = 10;
    int sum = AddNumbers(x, y);
    std::cout << "Sum is: " << sum << std::endl;
    return 0;
}"""
                    demo_graph = {
                        "nodes": [
                            {"id": "AddNumbers", "parameters": ["a", "b"], "local_variables": []},
                            {"id": "__main__", "parameters": [], "local_variables": ["x", "y", "sum"]},
                            {"id": "writeln", "parameters": ["val"], "local_variables": []}
                        ],
                        "links": [
                            {"source": "__main__", "target": "AddNumbers"},
                            {"source": "__main__", "target": "writeln"}
                        ]
                    }
                else:
                    demo_cpp = """#include <iostream>

int add_numbers(int a, int b) {
    return a + b;
}

int main() {
    int x = 5, y = 10;
    int sum = add_numbers(x, y);
    std::cout << "Sum is: " << sum << '\\n';
    return 0;
}"""
                    demo_graph = {
                        "nodes": [
                            {"id": "add_numbers", "parameters": ["a", "b"], "local_variables": []},
                            {"id": "main", "parameters": [], "local_variables": ["x", "y", "sum"]},
                            {"id": "printf", "parameters": ["fmt"], "local_variables": []}
                        ],
                        "links": [
                            {"source": "main", "target": "add_numbers"},
                            {"source": "main", "target": "printf"}
                        ]
                    }

                result_data = {
                    "generated_cpp": demo_cpp,
                    "dependency_graph_json": json.dumps(demo_graph),
                    "diff": "--- Legacy Source\\n+++ Modern C++\\n@@ Generated via AST Modernizer @@",
                    "functions_found": 2,
                    "edges_found": 2,
                    "status": "completed"
                }

            # Update Metrics
            engine_label = result_data.get("engine", "demo" if not backend_online else "llm")
            metric_funcs.metric("Functions", result_data.get("functions_found", 0))
            metric_edges.metric("Call Edges", result_data.get("edges_found", 0))
            metric_status.metric("Pipeline", f"Completed ✅ ({engine_label})")

            # ---------------------------------------------------------------
            # Results Tabs
            # ---------------------------------------------------------------
            tab_graph, tab_diff, tab_code = st.tabs([
                "🕸️ Dependency Call Graph",
                "⚖️ Side-by-Side Comparison",
                "⚡ Modern C++ Output"
            ])

            # Tab 1: Dependency Graph
            with tab_graph:
                st.subheader("Function Call Dependency Graph")
                try:
                    graph_json_str = result_data.get("dependency_graph_json", "{}")
                    graph_dict = json.loads(graph_json_str) if isinstance(graph_json_str, str) else graph_json_str

                    G = nx.DiGraph()
                    for node in graph_dict.get("nodes", []):
                        G.add_node(node.get("id"))
                    for link in graph_dict.get("links", []) or graph_dict.get("edges", []):
                        src = link.get("source")
                        dst = link.get("target")
                        if src and dst:
                            G.add_edge(src, dst)

                    if len(G.nodes) > 0:
                        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="#0E1117")
                        ax.set_facecolor("#0E1117")
                        pos = nx.spring_layout(G, seed=42)

                        nx.draw_networkx_nodes(
                            G, pos,
                            node_color="#8B5CF6",
                            node_size=2200,
                            alpha=0.9,
                            ax=ax
                        )
                        nx.draw_networkx_edges(
                            G, pos,
                            arrowstyle="->",
                            arrowsize=20,
                            edge_color="#06B6D4",
                            width=2,
                            ax=ax
                        )
                        nx.draw_networkx_labels(
                            G, pos,
                            font_color="#FFFFFF",
                            font_family="sans-serif",
                            font_size=10,
                            font_weight="bold",
                            ax=ax
                        )
                        plt.axis("off")
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.info("No dependency edges found in this source.")
                except Exception as ex:
                    st.warning(f"Could not render graph figure: {ex}")

            # Tab 2: Side-by-Side Diff
            with tab_diff:
                st.subheader("Side-by-Side Code Comparison")
                diff_col1, diff_col2 = st.columns(2)
                with diff_col1:
                    st.caption("Legacy Source")
                    st.code(edited_code, language=language)
                with diff_col2:
                    st.caption("Idiomatic Modern C++")
                    st.code(result_data["generated_cpp"], language="cpp")

                if result_data.get("diff"):
                    with st.expander("View Unified Diff Patch"):
                        st.code(result_data["diff"], language="diff")

            # Tab 3: Generated Code & Download
            with tab_code:
                st.subheader("Generated C++ Source")
                st.code(result_data["generated_cpp"], language="cpp")

                cpp_filename = os.path.splitext(filename)[0] + "_modern.cpp"
                st.download_button(
                    label=f"💾 Download {cpp_filename}",
                    data=result_data["generated_cpp"],
                    file_name=cpp_filename,
                    mime="text/x-c++src"
                )
