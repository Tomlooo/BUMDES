import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# === Konfigurasi dasar ===
st.set_page_config(page_title="Administrasi BUMDes", layout="wide")
st.title("📘 Sistem Akuntansi BUMDes")

# === Inisialisasi data awal ===
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Tanggal": "", "Keterangan": "", "Ref": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
    ])

if "neraca_saldo" not in st.session_state:
    st.session_state.neraca_saldo = pd.DataFrame([
        {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
    ])

# === Fungsi format rupiah ===
def format_rupiah(x):
    try:
        if x < 0:
            return f"(Rp {abs(x):,.0f})".replace(",", ".")
        return f"Rp {x:,.0f}".replace(",", ".")
    except Exception:
        return x

# === Fungsi AgGrid ===
def create_aggrid(df, key_suffix):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, resizable=True)
    gb.configure_grid_options(stopEditingWhenCellsLoseFocus=False)
    
    for col in df.columns:
        if "(Rp)" in col:
            gb.configure_column(col, type=["numericColumn"], valueFormatter="value ? value.toLocaleString() : ''")
    
    grid_options = gb.build()
    
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme="streamlit",
        height=400,
        key=f"aggrid_{key_suffix}"
    )
    
    return pd.DataFrame(grid_response["data"])

# === Styling ===
st.markdown("""
<style>
.ag-theme-streamlit {
    --ag-background-color: #F9FAFB;
    --ag-odd-row-background-color: #FFFFFF;
    --ag-header-background-color: #E9ECEF;
    --ag-border-color: #DDDDDD;
    --ag-header-foreground-color: #000000;
    --ag-font-family: "Inter", system-ui, sans-serif;
    --ag-font-size: 14px;
    --ag-row-hover-color: #EEF6ED;
    --ag-selected-row-background-color: #DDF0DC;
    --ag-cell-horizontal-padding: 10px;
    --ag-cell-vertical-padding: 6px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# === Tabs ===
tab1, tab2, tab3, tab4 = st.tabs([
    "🧾 Jurnal Umum", 
    "📚 Buku Besar", 
    "⚖️ Neraca Saldo",
    "📊 Laporan Keuangan"
])

# ========================================
# TAB 1: JURNAL UMUM (dari teman)
# ========================================
with tab1:
    st.header("🧾 Jurnal Umum")
    st.info("💡 Tekan Enter sekali untuk menyimpan perubahan otomatis.")

    gb = GridOptionsBuilder.from_dataframe(st.session_state.data)
    gb.configure_default_column(editable=True, resizable=True)
    gb.configure_grid_options(stopEditingWhenCellsLoseFocus=False)
    gb.configure_column("Tanggal", header_name="Tanggal (YYYY-MM-DD)")
    gb.configure_column("Keterangan", header_name="Keterangan")
    gb.configure_column("Ref", header_name="Ref (contoh: 101)")
    gb.configure_column("Debit (Rp)", type=["numericColumn"], valueFormatter="value ? value.toLocaleString() : ''")
    gb.configure_column("Kredit (Rp)", type=["numericColumn"], valueFormatter="value ? value.toLocaleString() : ''")

    grid_options = gb.build()

    grid_response = AgGrid(
        st.session_state.data,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme="streamlit",
        height=320,
        key="aggrid_jurnal"
    )

    new_df = pd.DataFrame(grid_response["data"])
    if not new_df.equals(st.session_state.data):
        st.session_state.data = new_df.copy()
        st.toast("💾 Perubahan tersimpan otomatis!", icon="💾")

    df_clean = new_df[new_df["Keterangan"].astype(str).str.strip() != ""]

    if not df_clean.empty:
        total_debit = df_clean["Debit (Rp)"].sum()
        total_kredit = df_clean["Kredit (Rp)"].sum()

        total_row = pd.DataFrame({
            "Tanggal": [""],
            "Keterangan": ["TOTAL"],
            "Ref": [""],
            "Debit (Rp)": [total_debit],
            "Kredit (Rp)": [total_kredit],
        })
        df_final = pd.concat([df_clean, total_row], ignore_index=True)

        st.write("### 📊 Hasil Jurnal")
        df_final_display = df_final.copy()
        df_final_display.index = range(1, len(df_final_display) + 1)
        df_final_display.index.name = "No"
        
        st.dataframe(df_final_display.style.format({
            "Debit (Rp)": format_rupiah,
            "Kredit (Rp)": format_rupiah
        }))

        def buat_pdf(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Jurnal Umum BUMDes", ln=True, align="C")
            pdf.ln(8)

            col_width = 190 / len(df.columns)
            for col in df.columns:
                pdf.cell(col_width, 10, col, border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", size=10)
            for _, row in df.iterrows():
                for item in row:
                    pdf.cell(col_width, 8, str(item), border=1, align="C")
                pdf.ln()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                tmp.seek(0)
                return tmp.read()

        pdf_data = buat_pdf(df_final)
        st.download_button(
            "📥 Download PDF",
            data=pdf_data,
            file_name="jurnal_umum.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Belum ada data valid di tabel.")

# ========================================
# TAB 2: BUKU BESAR
# ========================================
with tab2:
    st.header("📚 Buku Besar")
    st.info("Fitur ini sedang dalam pengembangan 🚧")

# ========================================
# TAB 3: NERACA SALDO
# ========================================
with tab3:
    st.header("⚖️ Neraca Saldo BUMDes")
    st.subheader("Periode: Januari 2025")
    st.info("💡 Masukkan data saldo akhir dari setiap akun di Buku Besar")

    # Tombol untuk menambah baris baru
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("➕ Tambah Baris", use_container_width=True):
            new_row = pd.DataFrame([{"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}])
            st.session_state.neraca_saldo = pd.concat([st.session_state.neraca_saldo, new_row], ignore_index=True)
            st.toast("✅ Baris baru ditambahkan!", icon="✅")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Hapus Baris Kosong", use_container_width=True):
            df_before = st.session_state.neraca_saldo.copy()
            st.session_state.neraca_saldo = st.session_state.neraca_saldo[
                st.session_state.neraca_saldo["Nama Akun"].astype(str).str.strip() != ""
            ].reset_index(drop=True)
            
            # Pastikan minimal ada 1 baris
            if len(st.session_state.neraca_saldo) == 0:
                st.session_state.neraca_saldo = pd.DataFrame([
                    {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
                ])
            
            if not df_before.equals(st.session_state.neraca_saldo):
                st.toast("🗑️ Baris kosong dihapus!", icon="🗑️")
                st.rerun()

    # Input data menggunakan AgGrid
    new_neraca = create_aggrid(st.session_state.neraca_saldo, "neraca")
    
    if not new_neraca.equals(st.session_state.neraca_saldo):
        st.session_state.neraca_saldo = new_neraca.copy()
        st.toast("💾 Data Neraca Saldo tersimpan!", icon="💾")

    # Filter data yang valid
    df_neraca_clean = new_neraca[new_neraca["Nama Akun"].astype(str).str.strip() != ""]

    if not df_neraca_clean.empty:
        total_debit = df_neraca_clean["Debit (Rp)"].sum()
        total_kredit = df_neraca_clean["Kredit (Rp)"].sum()

        total_row = pd.DataFrame({
            "No Akun": [""],
            "Nama Akun": ["Jumlah"],
            "Debit (Rp)": [total_debit],
            "Kredit (Rp)": [total_kredit]
        })

        df_neraca_final = pd.concat([df_neraca_clean, total_row], ignore_index=True)
        df_neraca_final.index = range(1, len(df_neraca_final) + 1)
        df_neraca_final.index.name = "No"

        st.write("### 📊 Hasil Neraca Saldo")
        st.dataframe(
            df_neraca_final.style.format({
                "Debit (Rp)": format_rupiah,
                "Kredit (Rp)": format_rupiah,
            }).apply(lambda x: ['font-weight: bold' if i == len(df_neraca_final) else '' for i in range(len(x))], axis=0),
            use_container_width=True
        )

        # HAPUS validasi balance - tidak perlu!
        # User input manual sudah seharusnya balance

        def buat_pdf_neraca(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Neraca Saldo BUMDes", ln=True, align="C")
            pdf.cell(200, 10, txt="Periode: Januari 2025", ln=True, align="C")
            pdf.ln(8)

            col_width = 190 / 4
            headers = ["No", "No Akun", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]
            for col in headers:
                pdf.cell(col_width if col != "No" else 15, 10, col, border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", size=10)
            for idx, row in df.iterrows():
                pdf.cell(15, 8, str(idx), border=1, align="C")
                pdf.cell(col_width, 8, str(row["No Akun"]), border=1, align="C")
                pdf.cell(col_width, 8, str(row["Nama Akun"]), border=1, align="C")
                pdf.cell(col_width, 8, format_rupiah(row["Debit (Rp)"]) if isinstance(row["Debit (Rp)"], (int, float)) else str(row["Debit (Rp)"]), border=1, align="R")
                pdf.cell(col_width, 8, format_rupiah(row["Kredit (Rp)"]) if isinstance(row["Kredit (Rp)"], (int, float)) else str(row["Kredit (Rp)"]), border=1, align="R")
                pdf.ln()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                tmp.seek(0)
                return tmp.read()

        pdf_neraca = buat_pdf_neraca(df_neraca_final)
        st.download_button(
            "📥 Download PDF Neraca Saldo",
            data=pdf_neraca,
            file_name="neraca_saldo.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Belum ada data valid di tabel Neraca Saldo.")
# ========================================
# TAB 4: LAPORAN KEUANGAN
# ========================================
with tab4:
    st.header("📊 Laporan Keuangan BUMDes")
    st.info("Fitur ini akan ditambahkan setelah Neraca Saldo selesai 🚧")
