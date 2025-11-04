import streamlit as st
import requests

API_URL = "http://localhost:8000/predict"  # or your deployed API endpoint

st.set_page_config(page_title="Corn Kernel Detector", page_icon="🌽", layout="centered")
st.title("🌽 Corn Kernel Quality Analyzer")

uploaded_file = st.file_uploader("Upload an image of Corn Kernels", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded image", use_container_width=True)

    if st.button("Analyze Kernels"):
        with st.spinner("Analyzing..."):
            try:
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(API_URL, files=files, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis complete ✅")
                    st.write(f"**Total Kernels:** {result['total_kernels']}")
                    st.write(f"**Good Kernels:** {result['good_kernels']}")
                    st.write(f"**Bad Kernels:** {result['bad_kernels']}")

                    if "annotated_image" in result:
                        st.image(result["annotated_image"], caption="Annotated Image", use_container_width=True)
                    else:
                        st.warning("⚠️ No annotated image returned from the API.")
                else:
                    st.error(f"API error {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                st.error("API request timed out ")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to API ")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
