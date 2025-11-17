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

if "pendapatan" not in st.session_state:
    st.session_state.pendapatan = pd.DataFrame([
        {"Jenis Pendapatan": "", "Jumlah (Rp)": 0}
    ])

if "beban" not in st.session_state:
    st.session_state.beban = pd.DataFrame([
        {"Jenis Beban": "", "Jumlah (Rp)": 0}
    ])

if "modal_data" not in st.session_state:
    st.session_state.modal_data = {
        "modal_awal": 0,
        "prive": 0
    }

if "aktiva_lancar" not in st.session_state:
    st.session_state.aktiva_lancar = pd.DataFrame([
        {"Item": "", "Jumlah (Rp)": 0}
    ])

if "aktiva_tetap" not in st.session_state:
    st.session_state.aktiva_tetap = pd.DataFrame([
        {"Item": "", "Jumlah (Rp)": 0}
    ])

if "kewajiban" not in st.session_state:
    st.session_state.kewajiban = pd.DataFrame([
        {"Item": "", "Jumlah (Rp)": 0}
    ])

if "arus_kas_operasi" not in st.session_state:
    st.session_state.arus_kas_operasi = pd.DataFrame([
        {"Aktivitas": "", "Jumlah (Rp)": 0}
    ])

if "arus_kas_investasi" not in st.session_state:
    st.session_state.arus_kas_investasi = pd.DataFrame([
        {"Aktivitas": "", "Jumlah (Rp)": 0}
    ])

if "arus_kas_pendanaan" not in st.session_state:
    st.session_state.arus_kas_pendanaan = pd.DataFrame([
        {"Aktivitas": "", "Jumlah (Rp)": 0}
    ])

# === Fungsi format rupiah ===
def format_rupiah(x):
    try:
        if x < 0:
            return f"({abs(x):,.0f})".replace(",", ".")
        return f"{x:,.0f}".replace(",", ".")
    except Exception:
        return x

# === Fungsi AgGrid ===
def create_aggrid(df, key_suffix, height=400):
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
        height=height,
        key=f"aggrid_{key_suffix}",
        reload_data=False
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
# TAB 1: JURNAL UMUM
# ========================================
with tab1:
    st.header("🧾 Jurnal Umum")
    st.info("💡 Tekan Enter sekali untuk menyimpan perubahan otomatis.")

    # Tombol tambah baris untuk Jurnal Umum
    if st.button("➕ Tambah Baris Jurnal", key="tambah_jurnal"):
        new_row = pd.DataFrame([{"Tanggal": "", "Keterangan": "", "Ref": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.rerun()

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
        key="aggrid_jurnal",
        reload_data=False
    )

    new_df = pd.DataFrame(grid_response["data"])
    if not new_df.equals(st.session_state.data):
        st.session_state.data = new_df.copy()

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
        if st.button("➕ Tambah Baris", key="tambah_neraca", use_container_width=True):
            new_row = pd.DataFrame([{"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}])
            st.session_state.neraca_saldo = pd.concat([st.session_state.neraca_saldo, new_row], ignore_index=True)
            st.rerun()
    
    with col2:
        if st.button("🗑️ Hapus Baris Kosong", key="hapus_neraca", use_container_width=True):
            st.session_state.neraca_saldo = st.session_state.neraca_saldo[
                st.session_state.neraca_saldo["Nama Akun"].astype(str).str.strip() != ""
            ].reset_index(drop=True)
            
            if len(st.session_state.neraca_saldo) == 0:
                st.session_state.neraca_saldo = pd.DataFrame([
                    {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
                ])
            st.rerun()

    # Input data menggunakan AgGrid
    new_neraca = create_aggrid(st.session_state.neraca_saldo, "neraca", height=400)
    
    if not new_neraca.equals(st.session_state.neraca_saldo):
        st.session_state.neraca_saldo = new_neraca.copy()

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

        # Fungsi PDF yang sudah diperbaiki
        def buat_pdf_neraca(df):
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, txt="Neraca Saldo BUMDes", ln=True, align="C")
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, txt="Periode: Januari 2025", ln=True, align="C")
            pdf.ln(5)

            # Table Header
            pdf.set_font("Arial", 'B', 10)
            col_widths = [15, 25, 70, 40, 40]
            headers = ["No", "No Akun", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, border=1, align="C")
            pdf.ln()

            # Table Content
            pdf.set_font("Arial", '', 9)
            for idx, row in df.iterrows():
                pdf.cell(col_widths[0], 8, str(idx), border=1, align="C")
                pdf.cell(col_widths[1], 8, str(row["No Akun"]), border=1, align="C")
                
                nama_akun = str(row["Nama Akun"])
                if len(nama_akun) > 35:
                    nama_akun = nama_akun[:32] + "..."
                pdf.cell(col_widths[2], 8, nama_akun, border=1, align="L")
                
                debit_val = row["Debit (Rp)"]
                if isinstance(debit_val, (int, float)) and debit_val != 0:
                    debit_text = format_rupiah(debit_val)
                else:
                    debit_text = "-"
                pdf.cell(col_widths[3], 8, debit_text, border=1, align="R")
                
                kredit_val = row["Kredit (Rp)"]
                if isinstance(kredit_val, (int, float)) and kredit_val != 0:
                    kredit_text = format_rupiah(kredit_val)
                else:
                    kredit_text = "-"
                pdf.cell(col_widths[4], 8, kredit_text, border=1, align="R")
                
                pdf.ln()

            pdf.ln(5)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 5, txt="Dicetak dari Sistem Akuntansi BUMDes", ln=True, align="C")

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
# TAB 4: LAPORAN KEUANGAN (SESUAI SCREENSHOT)
# ========================================
with tab4:
    st.header("📊 Laporan Keuangan BUMDes")
    st.subheader("Periode: Januari 2025")

    # ========================================
    # 1. LAPORAN LABA/RUGI
    # ========================================
    st.markdown("---")
    st.markdown("### 📈 Laporan Laba/Rugi")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("#### Input Pendapatan:")
        if st.button("➕ Tambah Pendapatan", key="tambah_pendapatan"):
            new_row = pd.DataFrame([{"Jenis Pendapatan": "", "Jumlah (Rp)": 0}])
            st.session_state.pendapatan = pd.concat([st.session_state.pendapatan, new_row], ignore_index=True)
            st.rerun()
        
        new_pendapatan = create_aggrid(st.session_state.pendapatan, "pendapatan", height=250)
        if not new_pendapatan.equals(st.session_state.pendapatan):
            st.session_state.pendapatan = new_pendapatan.copy()

    with col2:
        st.write("#### Input Beban-Beban:")
        if st.button("➕ Tambah Beban", key="tambah_beban"):
            new_row = pd.DataFrame([{"Jenis Beban": "", "Jumlah (Rp)": 0}])
            st.session_state.beban = pd.concat([st.session_state.beban, new_row], ignore_index=True)
            st.rerun()
        
        new_beban = create_aggrid(st.session_state.beban, "beban", height=250)
        if not new_beban.equals(st.session_state.beban):
            st.session_state.beban = new_beban.copy()

    df_pendapatan_clean = new_pendapatan[new_pendapatan["Jenis Pendapatan"].astype(str).str.strip() != ""]
    df_beban_clean = new_beban[new_beban["Jenis Beban"].astype(str).str.strip() != ""]

    if not df_pendapatan_clean.empty or not df_beban_clean.empty:
        total_pendapatan = df_pendapatan_clean["Jumlah (Rp)"].sum()
        total_beban = df_beban_clean["Jumlah (Rp)"].sum()
        laba_bersih = total_pendapatan - total_beban

        st.write("### 📊 Hasil Laporan Laba/Rugi")
        
        # Format sesuai screenshot Excel (3 kolom)
        result_data = []
        result_data.append({"": "Laporan Laba/Rugi", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "BUMDes", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "Pendapatan:", "Kolom2": "", "Jumlah": ""})
        
        for idx, row in df_pendapatan_clean.iterrows():
            result_data.append({"": f"{idx+1}. {row['Jenis Pendapatan']}", "Kolom2": "", "Jumlah": row["Jumlah (Rp)"]})
        
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "Total Pendapatan", "Kolom2": "", "Jumlah": total_pendapatan})
        result_data.append({"": "Beban-Beban:", "Kolom2": "", "Jumlah": ""})
        
        for idx, row in df_beban_clean.iterrows():
            result_data.append({"": f"{idx+1}. {row['Jenis Beban']}", "Kolom2": "", "Jumlah": row["Jumlah (Rp)"]})
        
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "Total Beban", "Kolom2": "", "Jumlah": total_beban})
        result_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        result_data.append({"": "Laba Bersih", "Kolom2": "", "Jumlah": laba_bersih})

        df_labarugi = pd.DataFrame(result_data)
        
        st.dataframe(
            df_labarugi.style.format({"Jumlah": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x})
            .set_properties(**{'text-align': 'left'}, subset=[''])
            .set_properties(**{'text-align': 'right'}, subset=['Jumlah']),
            use_container_width=True,
            hide_index=True
        )

    # ========================================
    # 2. LAPORAN PERUBAHAN MODAL
    # ========================================
    st.markdown("---")
    st.markdown("### 💰 Laporan Perubahan Modal")
    
    col1, col2 = st.columns(2)
    with col1:
        modal_awal = st.number_input("Modal Awal (Rp)", value=st.session_state.modal_data["modal_awal"], step=100000, key="modal_awal_input")
    with col2:
        prive = st.number_input("Prive (Rp)", value=st.session_state.modal_data["prive"], step=100000, key="prive_input")
    
    if modal_awal != st.session_state.modal_data["modal_awal"] or prive != st.session_state.modal_data["prive"]:
        st.session_state.modal_data["modal_awal"] = modal_awal
        st.session_state.modal_data["prive"] = prive

    if not df_pendapatan_clean.empty or not df_beban_clean.empty:
        modal_akhir = modal_awal + laba_bersih - prive

        st.write("### 📊 Hasil Laporan Perubahan Modal")
        
        # Format sesuai screenshot (Prive di kolom TENGAH!)
        modal_data = []
        modal_data.append({"": "Laporan Perubahan Modal", "Kolom2": "", "Jumlah": ""})
        modal_data.append({"": "BUMDes", "Kolom2": "", "Jumlah": ""})
        modal_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        modal_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        modal_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        modal_data.append({"": "Modal Awal", "Kolom2": "", "Jumlah": modal_awal})
        modal_data.append({"": "", "Kolom2": "", "Jumlah": ""})
        modal_data.append({"": "Laba Bersih", "Kolom2": "", "Jumlah": laba_bersih})
        modal_data.append({"": "Prive", "Kolom2": prive, "Jumlah": ""})  # Prive di kolom tengah!
        modal_data.append({"": "Modal Akhir", "Kolom2": "", "Jumlah": modal_akhir})

        df_modal = pd.DataFrame(modal_data)

        st.dataframe(
            df_modal.style.format({
                "Kolom2": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x,
                "Jumlah": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
            })
            .set_properties(**{'text-align': 'left'}, subset=[''])
            .set_properties(**{'text-align': 'right'}, subset=['Kolom2', 'Jumlah']),
            use_container_width=True,
            hide_index=True
        )

        # ========================================
        # 3. LAPORAN NERACA
        # ========================================
        st.markdown("---")
        st.markdown("### 🏦 Laporan Neraca")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Aktiva Lancar:")
            if st.button("➕ Tambah Aktiva Lancar", key="tambah_aktiva_lancar"):
                new_row = pd.DataFrame([{"Item": "", "Jumlah (Rp)": 0}])
                st.session_state.aktiva_lancar = pd.concat([st.session_state.aktiva_lancar, new_row], ignore_index=True)
                st.rerun()
            
            new_aktiva_lancar = create_aggrid(st.session_state.aktiva_lancar, "aktiva_lancar", height=200)
            if not new_aktiva_lancar.equals(st.session_state.aktiva_lancar):
                st.session_state.aktiva_lancar = new_aktiva_lancar.copy()

            st.write("#### Aktiva Tetap:")
            if st.button("➕ Tambah Aktiva Tetap", key="tambah_aktiva_tetap"):
                new_row = pd.DataFrame([{"Item": "", "Jumlah (Rp)": 0}])
                st.session_state.aktiva_tetap = pd.concat([st.session_state.aktiva_tetap, new_row], ignore_index=True)
                st.rerun()
            
            new_aktiva_tetap = create_aggrid(st.session_state.aktiva_tetap, "aktiva_tetap", height=200)
            if not new_aktiva_tetap.equals(st.session_state.aktiva_tetap):
                st.session_state.aktiva_tetap = new_aktiva_tetap.copy()

        with col2:
            st.write("#### Kewajiban:")
            if st.button("➕ Tambah Kewajiban", key="tambah_kewajiban"):
                new_row = pd.DataFrame([{"Item": "", "Jumlah (Rp)": 0}])
                st.session_state.kewajiban = pd.concat([st.session_state.kewajiban, new_row], ignore_index=True)
                st.rerun()
            
            new_kewajiban = create_aggrid(st.session_state.kewajiban, "kewajiban", height=200)
            if not new_kewajiban.equals(st.session_state.kewajiban):
                st.session_state.kewajiban = new_kewajiban.copy()

        df_aktiva_lancar_clean = new_aktiva_lancar[new_aktiva_lancar["Item"].astype(str).str.strip() != ""]
        df_aktiva_tetap_clean = new_aktiva_tetap[new_aktiva_tetap["Item"].astype(str).str.strip() != ""]
        df_kewajiban_clean = new_kewajiban[new_kewajiban["Item"].astype(str).str.strip() != ""]

        jml_aktiva_lancar = df_aktiva_lancar_clean["Jumlah (Rp)"].sum()
        jml_aktiva_tetap = df_aktiva_tetap_clean["Jumlah (Rp)"].sum()
        jml_aktiva = jml_aktiva_lancar + jml_aktiva_tetap
        
        jml_kewajiban = df_kewajiban_clean["Jumlah (Rp)"].sum()
        jml_ekuitas = modal_akhir
        jml_kewajiban_ekuitas = jml_kewajiban + jml_ekuitas

        st.write("### 📊 Hasil Laporan Neraca")
        
        # Format sesuai screenshot (4 kolom)
        neraca_data = []
        neraca_data.append({"Aktiva": "Laporan Neraca", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "BUMDes", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "Aktiva", "Jumlah1": "", "Passiva": "Passiva", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "Aktiva Lancar:", "Jumlah1": "", "Passiva": "Kewajiban:", "Jumlah2": ""})
        
        max_rows = max(len(df_aktiva_lancar_clean), len(df_kewajiban_clean))
        for i in range(max_rows):
            aktiva_item = df_aktiva_lancar_clean.iloc[i]["Item"] if i < len(df_aktiva_lancar_clean) else ""
            aktiva_val = df_aktiva_lancar_clean.iloc[i]["Jumlah (Rp)"] if i < len(df_aktiva_lancar_clean) else ""
            kewajiban_item = df_kewajiban_clean.iloc[i]["Item"] if i < len(df_kewajiban_clean) else ""
            kewajiban_val = df_kewajiban_clean.iloc[i]["Jumlah (Rp)"] if i < len(df_kewajiban_clean) else ""
            
            neraca_data.append({
                "Aktiva": aktiva_item,
                "Jumlah1": aktiva_val,
                "Passiva": kewajiban_item,
                "Jumlah2": kewajiban_val
            })
        
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "Jml aktiva lancar", "Jumlah1": jml_aktiva_lancar, "Passiva": "Ekuitas:", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "Modal", "Jumlah2": modal_awal})
        neraca_data.append({"Aktiva": "Aktiva Tetap:", "Jumlah1": "", "Passiva": "Laba", "Jumlah2": laba_bersih})
        
        for idx, row in df_aktiva_tetap_clean.iterrows():
            neraca_data.append({
                "Aktiva": row['Item'],
                "Jumlah1": row["Jumlah (Rp)"],
                "Passiva": "Prive" if idx == df_aktiva_tetap_clean.index[0] else "",
                "Jumlah2": f"({format_rupiah(prive)})" if idx == df_aktiva_tetap_clean.index[0] else ""  # Kurung!
            })
        
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
        neraca_data.append({"Aktiva": "Jml Aktiva", "Jumlah1": jml_aktiva, "Passiva": "Jml Kewajiban&Ekuitas", "Jumlah2": jml_kewajiban_ekuitas})

        df_neraca_lap = pd.DataFrame(neraca_data)

        st.dataframe(
            df_neraca_lap.style.format({
                "Jumlah1": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x,
                "Jumlah2": lambda x: x if isinstance(x, str) and "(" in x else (format_rupiah(x) if isinstance(x, (int, float)) else x)
            })
            .set_properties(**{'text-align': 'left'}, subset=['Aktiva', 'Passiva'])
            .set_properties(**{'text-align': 'right'}, subset=['Jumlah1', 'Jumlah2']),
            use_container_width=True,
            hide_index=True
        )

        # ========================================
        # 4. LAPORAN ARUS KAS
        # ========================================
        st.markdown("---")
        st.markdown("### 💸 Laporan Arus Kas")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("#### Arus Kas Operasi:")
            if st.button("➕ Tambah Operasi", key="tambah_operasi"):
                new_row = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                st.session_state.arus_kas_operasi = pd.concat([st.session_state.arus_kas_operasi, new_row], ignore_index=True)
                st.rerun()
            
            new_arus_operasi = create_aggrid(st.session_state.arus_kas_operasi, "operasi", height=250)
            if not new_arus_operasi.equals(st.session_state.arus_kas_operasi):
                st.session_state.arus_kas_operasi = new_arus_operasi.copy()

        with col2:
            st.write("#### Arus Kas Investasi:")
            if st.button("➕ Tambah Investasi", key="tambah_investasi"):
                new_row = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                st.session_state.arus_kas_investasi = pd.concat([st.session_state.arus_kas_investasi, new_row], ignore_index=True)
                st.rerun()
            
            new_arus_investasi = create_aggrid(st.session_state.arus_kas_investasi, "investasi", height=250)
            if not new_arus_investasi.equals(st.session_state.arus_kas_investasi):
                st.session_state.arus_kas_investasi = new_arus_investasi.copy()

        with col3:
            st.write("#### Arus Kas Pendanaan:")
            if st.button("➕ Tambah Pendanaan", key="tambah_pendanaan"):
                new_row = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                st.session_state.arus_kas_pendanaan = pd.concat([st.session_state.arus_kas_pendanaan, new_row], ignore_index=True)
                st.rerun()
            
            new_arus_pendanaan = create_aggrid(st.session_state.arus_kas_pendanaan, "pendanaan", height=250)
            if not new_arus_pendanaan.equals(st.session_state.arus_kas_pendanaan):
                st.session_state.arus_kas_pendanaan = new_arus_pendanaan.copy()

        df_operasi_clean = new_arus_operasi[new_arus_operasi["Aktivitas"].astype(str).str.strip() != ""]
        df_investasi_clean = new_arus_investasi[new_arus_investasi["Aktivitas"].astype(str).str.strip() != ""]
        df_pendanaan_clean = new_arus_pendanaan[new_arus_pendanaan["Aktivitas"].astype(str).str.strip() != ""]

        if not df_operasi_clean.empty or not df_investasi_clean.empty or not df_pendanaan_clean.empty:
            st.write("### 📊 Hasil Laporan Arus Kas")
            
            # Format sesuai screenshot (3 kolom)
            arus_kas_data = []
            arus_kas_data.append({"": "Laporan Arus Kas", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "BUMDes", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "Arus Kas Operasi:", "Kolom2": "", "Jumlah": ""})
            
            for _, row in df_operasi_clean.iterrows():
                arus_kas_data.append({"": row['Aktivitas'], "Kolom2": "", "Jumlah": row["Jumlah (Rp)"]})
            
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "Arus Kas Investasi:", "Kolom2": "", "Jumlah": ""})
            
            for _, row in df_investasi_clean.iterrows():
                arus_kas_data.append({"": row['Aktivitas'], "Kolom2": "", "Jumlah": row["Jumlah (Rp)"]})
            
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "", "Kolom2": "", "Jumlah": ""})
            arus_kas_data.append({"": "Arus Kas Pendanaan:", "Kolom2": "", "Jumlah": ""})
            
            for _, row in df_pendanaan_clean.iterrows():
                arus_kas_data.append({"": row['Aktivitas'], "Kolom2": "", "Jumlah": row["Jumlah (Rp)"]})

            df_arus_kas = pd.DataFrame(arus_kas_data)

            st.dataframe(
                df_arus_kas.style.format({
                    "Jumlah": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
                })
                .set_properties(**{'text-align': 'left'}, subset=[''])
                .set_properties(**{'text-align': 'right'}, subset=['Jumlah']),
                use_container_width=True,
                hide_index=True
            )
