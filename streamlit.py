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
# TAB 3: NERACA SALDO (DENGAN DROPDOWN NAMA AKUN)
# ========================================
with tab3:
    st.header("💵 Neraca Saldo BUMDes")
    
    # --- Selector Periode ---
    col1, col2 = st.columns(2)
    
    bulan_dict = {
        "01": "Januari", "02": "Februari", "03": "Maret",
        "04": "April", "05": "Mei", "06": "Juni",
        "07": "Juli", "08": "Agustus", "09": "September",
        "10": "Oktober", "11": "November", "12": "Desember"
    }
    
    with col1:
        bulan_neraca = st.selectbox(
            "Pilih Bulan", 
            options=[
                ("01", "Januari"), ("02", "Februari"), ("03", "Maret"),
                ("04", "April"), ("05", "Mei"), ("06", "Juni"),
                ("07", "Juli"), ("08", "Agustus"), ("09", "September"),
                ("10", "Oktober"), ("11", "November"), ("12", "Desember")
            ],
            format_func=lambda x: x[1],
            key="bulan_neraca"
        )[0]
    
    with col2:
        tahun_neraca = st.number_input(
            "Tahun", 
            min_value=2000, 
            max_value=2100, 
            value=2025,
            step=1,
            key="tahun_neraca"
        )
    
    st.subheader(f"Periode: {bulan_dict[bulan_neraca]} {tahun_neraca}")
    
    st.info("💡 Masukkan data saldo akhir dari setiap akun di Buku Besar. Klik 'Tambah Baris' untuk menambah data baru.")

    # Counter untuk force refresh
    if "neraca_refresh_counter" not in st.session_state:
        st.session_state.neraca_refresh_counter = 0
    
    # --- Ambil daftar akun dari Buku Besar (AMAN) ---
    daftar_akun_values = []
    
    # Cek keberadaan buku_besar dengan aman
    try:
        if hasattr(st.session_state, 'buku_besar') and st.session_state.buku_besar:
            for akun_no, akun_data in st.session_state.buku_besar.items():
                if isinstance(akun_data, dict) and "nama_akun" in akun_data:
                    daftar_akun_values.append(akun_data["nama_akun"])
    except AttributeError:
        # Jika buku_besar belum ada, buat kosong
        st.session_state.buku_besar = {}
    
    # Tombol kontrol
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Tambah 1 Baris", key="tambah_neraca_1", use_container_width=True):
            new_row = pd.DataFrame([{"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}])
            st.session_state.neraca_saldo = pd.concat([st.session_state.neraca_saldo, new_row], ignore_index=True)
            st.session_state.neraca_refresh_counter += 1
            st.rerun()
    
    with col2:
        if st.button("➕➕ Tambah 5 Baris", key="tambah_neraca_5", use_container_width=True):
            new_rows = pd.DataFrame([
                {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0},
                {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0},
                {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0},
                {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0},
                {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
            ])
            st.session_state.neraca_saldo = pd.concat([st.session_state.neraca_saldo, new_rows], ignore_index=True)
            st.session_state.neraca_refresh_counter += 1
            st.rerun()
    
    with col3:
        if st.button("🗑️ Hapus Kosong", key="hapus_neraca_kosong", use_container_width=True):
            st.session_state.neraca_saldo = st.session_state.neraca_saldo[
                st.session_state.neraca_saldo["Nama Akun"].astype(str).str.strip() != ""
            ].reset_index(drop=True)
            
            if len(st.session_state.neraca_saldo) == 0:
                st.session_state.neraca_saldo = pd.DataFrame([
                    {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
                ])
            st.session_state.neraca_refresh_counter += 1
            st.rerun()

    # Info counter
    total_rows = len(st.session_state.neraca_saldo)
    filled_rows = len(st.session_state.neraca_saldo[st.session_state.neraca_saldo["Nama Akun"].astype(str).str.strip() != ""])
    st.caption(f"📊 Total Baris: {total_rows} | Terisi: {filled_rows} | Kosong: {total_rows - filled_rows}")

    # --- Sistem Penghapusan dengan Checkbox ---
    df_terisi = st.session_state.neraca_saldo[st.session_state.neraca_saldo["Nama Akun"].astype(str).str.strip() != ""]
    
    if len(df_terisi) > 0:
        with st.expander("🗑️ Hapus Baris Tertentu", expanded=False):
            st.write("**Pilih baris yang ingin dihapus:**")
            
            rows_to_delete = []
            
            for idx in df_terisi.index:
                row = df_terisi.loc[idx]
                col_check, col_info = st.columns([1, 9])
                
                with col_check:
                    if st.checkbox("", key=f"check_del_{idx}_{st.session_state.neraca_refresh_counter}"):
                        rows_to_delete.append(idx)
                
                with col_info:
                    st.text(f"No: {row['No Akun']} | {row['Nama Akun']} | Debit: {format_rupiah(row['Debit (Rp)'])} | Kredit: {format_rupiah(row['Kredit (Rp)'])}")
            
            if rows_to_delete:
                if st.button(f"🗑️ Hapus {len(rows_to_delete)} Baris", key="confirm_delete", use_container_width=True):
                    st.session_state.neraca_saldo = st.session_state.neraca_saldo.drop(rows_to_delete).reset_index(drop=True)
                    
                    if len(st.session_state.neraca_saldo) == 0:
                        st.session_state.neraca_saldo = pd.DataFrame([
                            {"No Akun": "", "Nama Akun": "", "Debit (Rp)": 0, "Kredit (Rp)": 0}
                        ])
                    
                    st.session_state.neraca_refresh_counter += 1
                    st.success("✅ Baris berhasil dihapus!")
                    st.rerun()

    st.markdown("---")

    # --- AgGrid dengan Dropdown Nama Akun ---
    aggrid_key = f"neraca_{st.session_state.neraca_refresh_counter}"
    
    gb = GridOptionsBuilder.from_dataframe(st.session_state.neraca_saldo)
    gb.configure_default_column(editable=True, resizable=True)
    gb.configure_grid_options(stopEditingWhenCellsLoseFocus=False)
    
    # DROPDOWN untuk kolom Nama Akun (dari Buku Besar)
    if daftar_akun_values:
        gb.configure_column(
            "Nama Akun",
            editable=True,
            cellEditor="agSelectCellEditor",
            cellEditorParams={
                "values": daftar_akun_values
            }
        )
    
    # Konfigurasi kolom angka
    for col in st.session_state.neraca_saldo.columns:
        if "(Rp)" in col:
            gb.configure_column(col, type=["numericColumn"], valueFormatter="value ? value.toLocaleString() : ''")
    
    grid_options = gb.build()
    
    grid_response = AgGrid(
        st.session_state.neraca_saldo,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme="streamlit",
        height=300,
        key=aggrid_key,
        reload_data=True
    )
    
    new_neraca = pd.DataFrame(grid_response["data"])
    if not new_neraca.equals(st.session_state.neraca_saldo):
        st.session_state.neraca_saldo = new_neraca.copy()

    # Filter data valid
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

        # PDF Export
        def buat_pdf_neraca(df, bulan, tahun):
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, txt="Neraca Saldo BUMDes", ln=True, align="C")
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, txt=f"Periode: {bulan_dict[bulan]} {tahun}", ln=True, align="C")
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 10)
            col_widths = [15, 25, 70, 40, 40]
            headers = ["No", "No Akun", "Nama Akun", "Debit (Rp)", "Kredit (Rp)"]
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", '', 9)
            for idx, row in df.iterrows():
                pdf.cell(col_widths[0], 8, str(idx), border=1, align="C")
                pdf.cell(col_widths[1], 8, str(row["No Akun"]), border=1, align="C")
                
                nama_akun = str(row["Nama Akun"])
                if len(nama_akun) > 35:
                    nama_akun = nama_akun[:32] + "..."
                pdf.cell(col_widths[2], 8, nama_akun, border=1, align="L")
                
                debit_val = row["Debit (Rp)"]
                debit_text = format_rupiah(debit_val) if isinstance(debit_val, (int, float)) and debit_val != 0 else "-"
                pdf.cell(col_widths[3], 8, debit_text, border=1, align="R")
                
                kredit_val = row["Kredit (Rp)"]
                kredit_text = format_rupiah(kredit_val) if isinstance(kredit_val, (int, float)) and kredit_val != 0 else "-"
                pdf.cell(col_widths[4], 8, kredit_text, border=1, align="R")
                
                pdf.ln()

            pdf.ln(5)
            pdf.set_font("Arial", 'I', 8)
            pdf.cell(0, 5, txt="Dicetak dari Sistem Akuntansi BUMDes", ln=True, align="C")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                tmp.seek(0)
                return tmp.read()

        pdf_neraca = buat_pdf_neraca(df_neraca_final, bulan_neraca, tahun_neraca)
        st.download_button(
            "📥 Download PDF Neraca Saldo",
            data=pdf_neraca,
            file_name=f"neraca_saldo_{bulan_neraca}_{tahun_neraca}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Belum ada data valid di tabel Neraca Saldo.")

# ========================================
# TAB 4: LAPORAN KEUANGAN (AUTO-GENERATE + SUB-TABS)
# ========================================
with tab4:
    st.header("📊 Laporan Keuangan BUMDes")
    
    # --- Selector Periode ---
    col1, col2 = st.columns(2)
    
    bulan_dict = {
        "01": "Januari", "02": "Februari", "03": "Maret",
        "04": "April", "05": "Mei", "06": "Juni",
        "07": "Juli", "08": "Agustus", "09": "September",
        "10": "Oktober", "11": "November", "12": "Desember"
    }
    
    with col1:
        bulan_laporan = st.selectbox(
            "Pilih Bulan", 
            options=[
                ("01", "Januari"), ("02", "Februari"), ("03", "Maret"),
                ("04", "April"), ("05", "Mei"), ("06", "Juni"),
                ("07", "Juli"), ("08", "Agustus"), ("09", "September"),
                ("10", "Oktober"), ("11", "November"), ("12", "Desember")
            ],
            format_func=lambda x: x[1],
            key="bulan_laporan"
        )[0]
    
    with col2:
        tahun_laporan = st.number_input(
            "Tahun", 
            min_value=2000, 
            max_value=2100, 
            value=2025,
            step=1,
            key="tahun_laporan"
        )
    
    st.subheader(f"Periode: {bulan_dict[bulan_laporan]} {tahun_laporan}")
    
    st.info("💡 Laporan keuangan dibuat otomatis dari data Neraca Saldo. Pastikan Neraca Saldo sudah terisi dengan benar.")

    # --- Ambil data dari Neraca Saldo ---
    df_neraca = st.session_state.neraca_saldo[
        st.session_state.neraca_saldo["Nama Akun"].astype(str).str.strip() != ""
    ]
    
    if df_neraca.empty:
        st.warning("⚠️ Belum ada data di Neraca Saldo. Silakan isi Neraca Saldo terlebih dahulu.")
    else:
        # Klasifikasi akun berdasarkan nama
        pendapatan_list = []
        beban_list = []
        kas = 0
        aktiva_lancar_list = []
        aktiva_tetap_list = []
        modal_awal = 0
        kewajiban_list = []
        
        for _, row in df_neraca.iterrows():
            nama_akun = str(row["Nama Akun"]).lower()
            debit = row["Debit (Rp)"]
            kredit = row["Kredit (Rp)"]
            
            # Klasifikasi berdasarkan nama akun
            if "pendapatan" in nama_akun or "penjualan" in nama_akun:
                pendapatan_list.append({"nama": row["Nama Akun"], "jumlah": kredit})
            elif "beban" in nama_akun or "biaya" in nama_akun:
                beban_list.append({"nama": row["Nama Akun"], "jumlah": debit})
            elif "kas" in nama_akun:
                kas = debit
                aktiva_lancar_list.append({"nama": row["Nama Akun"], "jumlah": debit})
            elif "perlengkapan" in nama_akun or "piutang" in nama_akun:
                aktiva_lancar_list.append({"nama": row["Nama Akun"], "jumlah": debit})
            elif "peralatan" in nama_akun or "gedung" in nama_akun or "kendaraan" in nama_akun:
                aktiva_tetap_list.append({"nama": row["Nama Akun"], "jumlah": debit})
            elif "modal" in nama_akun and "prive" not in nama_akun:
                modal_awal = kredit
            elif "hutang" in nama_akun or "utang" in nama_akun:
                kewajiban_list.append({"nama": row["Nama Akun"], "jumlah": kredit})
        
        # Hitung totals
        total_pendapatan = sum([x["jumlah"] for x in pendapatan_list])
        total_beban = sum([x["jumlah"] for x in beban_list])
        laba_bersih = total_pendapatan - total_beban
        
        total_aktiva_lancar = sum([x["jumlah"] for x in aktiva_lancar_list])
        total_aktiva_tetap = sum([x["jumlah"] for x in aktiva_tetap_list])
        total_aktiva = total_aktiva_lancar + total_aktiva_tetap
        
        total_kewajiban = sum([x["jumlah"] for x in kewajiban_list])
        modal_akhir = modal_awal + laba_bersih
        total_passiva = total_kewajiban + modal_akhir
        
        # === SUB-TABS untuk 3 Laporan ===
        subtab1, subtab2, subtab3 = st.tabs([
            "📈 Laba/Rugi",
            "🏦 Neraca", 
            "💸 Arus Kas"
        ])
        
        # ========================================
        # SUB-TAB 1: LAPORAN LABA/RUGI
        # ========================================
        with subtab1:
            st.markdown("### 📈 Laporan Laba/Rugi")
            st.markdown(f"**BUMDes - {bulan_dict[bulan_laporan]} {tahun_laporan}**")
            st.markdown("---")
            
            # Format data untuk tabel
            labarugi_data = []
            labarugi_data.append({"Keterangan": "Pendapatan:", "Jumlah": ""})
            
            for idx, item in enumerate(pendapatan_list, 1):
                labarugi_data.append({"Keterangan": f"  {idx}. {item['nama']}", "Jumlah": item['jumlah']})
            
            labarugi_data.append({"Keterangan": "", "Jumlah": ""})
            labarugi_data.append({"Keterangan": "Total Pendapatan", "Jumlah": total_pendapatan})
            labarugi_data.append({"Keterangan": "", "Jumlah": ""})
            labarugi_data.append({"Keterangan": "Beban-Beban:", "Jumlah": ""})
            
            for idx, item in enumerate(beban_list, 1):
                labarugi_data.append({"Keterangan": f"  {idx}. {item['nama']}", "Jumlah": item['jumlah']})
            
            labarugi_data.append({"Keterangan": "", "Jumlah": ""})
            labarugi_data.append({"Keterangan": "Total Beban", "Jumlah": total_beban})
            labarugi_data.append({"Keterangan": "", "Jumlah": ""})
            labarugi_data.append({"Keterangan": "Laba Bersih", "Jumlah": laba_bersih})
            
            df_labarugi = pd.DataFrame(labarugi_data)
            
            st.dataframe(
                df_labarugi.style.format({
                    "Jumlah": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
                })
                .apply(lambda x: ['font-weight: bold' if 'Total' in str(df_labarugi.loc[i, 'Keterangan']) or 'Laba Bersih' in str(df_labarugi.loc[i, 'Keterangan']) else '' for i in range(len(x))], axis=0)
                .set_properties(**{'text-align': 'left'}, subset=['Keterangan'])
                .set_properties(**{'text-align': 'right'}, subset=['Jumlah']),
                use_container_width=True,
                hide_index=True
            )
            
            # PDF Export Laba/Rugi
            def buat_pdf_labarugi(df, bulan, tahun):
                pdf = FPDF()
                pdf.add_page()
                
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, txt="Laporan Laba/Rugi", ln=True, align="C")
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 8, txt="BUMDes", ln=True, align="C")
                pdf.cell(0, 8, txt=f"Periode: {bulan_dict[bulan]} {tahun}", ln=True, align="C")
                pdf.ln(5)

                pdf.set_font("Arial", 'B', 10)
                col_widths = [120, 60]
                headers = ["Keterangan", "Jumlah (Rp)"]
                
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, border=1, align="C")
                pdf.ln()

                pdf.set_font("Arial", '', 9)
                for _, row in df.iterrows():
                    # Bold untuk baris total
                    is_bold = 'Total' in str(row['Keterangan']) or 'Laba' in str(row['Keterangan'])
                    if is_bold:
                        pdf.set_font("Arial", 'B', 9)
                    
                    pdf.cell(col_widths[0], 8, str(row["Keterangan"]), border=1, align="L")
                    
                    jumlah_text = format_rupiah(row["Jumlah"]) if isinstance(row["Jumlah"], (int, float)) else ""
                    pdf.cell(col_widths[1], 8, jumlah_text, border=1, align="R")
                    pdf.ln()
                    
                    if is_bold:
                        pdf.set_font("Arial", '', 9)

                pdf.ln(5)
                pdf.set_font("Arial", 'I', 8)
                pdf.cell(0, 5, txt="Dicetak dari Sistem Akuntansi BUMDes", ln=True, align="C")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    pdf.output(tmp.name)
                    tmp.seek(0)
                    return tmp.read()

            pdf_labarugi = buat_pdf_labarugi(df_labarugi, bulan_laporan, tahun_laporan)
            st.download_button(
                "📥 Download PDF Laba/Rugi",
                data=pdf_labarugi,
                file_name=f"laporan_labarugi_{bulan_laporan}_{tahun_laporan}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # ========================================
        # SUB-TAB 2: LAPORAN NERACA
        # ========================================
        with subtab2:
            st.markdown("### 🏦 Laporan Neraca")
            st.markdown(f"**BUMDes - {bulan_dict[bulan_laporan]} {tahun_laporan}**")
            st.markdown("---")
            
            # Format data untuk tabel (4 kolom)
            neraca_data = []
            neraca_data.append({"Aktiva": "Aktiva", "Jumlah1": "", "Passiva": "Passiva", "Jumlah2": ""})
            neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
            neraca_data.append({"Aktiva": "Aktiva Lancar:", "Jumlah1": "", "Passiva": "Kewajiban:", "Jumlah2": ""})
            
            # Aktiva Lancar & Kewajiban
            max_rows = max(len(aktiva_lancar_list), len(kewajiban_list))
            for i in range(max_rows):
                aktiva_item = aktiva_lancar_list[i]["nama"] if i < len(aktiva_lancar_list) else ""
                aktiva_val = aktiva_lancar_list[i]["jumlah"] if i < len(aktiva_lancar_list) else ""
                kewajiban_item = kewajiban_list[i]["nama"] if i < len(kewajiban_list) else ""
                kewajiban_val = kewajiban_list[i]["jumlah"] if i < len(kewajiban_list) else ""
                
                neraca_data.append({
                    "Aktiva": f"  {aktiva_item}",
                    "Jumlah1": aktiva_val,
                    "Passiva": f"  {kewajiban_item}",
                    "Jumlah2": kewajiban_val
                })
            
            neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
            neraca_data.append({"Aktiva": "Jml aktiva lancar", "Jumlah1": total_aktiva_lancar, "Passiva": "Ekuitas:", "Jumlah2": ""})
            neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "  Modal", "Jumlah2": modal_awal})
            neraca_data.append({"Aktiva": "Aktiva Tetap:", "Jumlah1": "", "Passiva": "  Laba", "Jumlah2": laba_bersih})
            
            # Aktiva Tetap
            for idx, item in enumerate(aktiva_tetap_list):
                neraca_data.append({
                    "Aktiva": f"  {item['nama']}",
                    "Jumlah1": item['jumlah'],
                    "Passiva": "",
                    "Jumlah2": ""
                })
            
            neraca_data.append({"Aktiva": "", "Jumlah1": "", "Passiva": "", "Jumlah2": ""})
            neraca_data.append({"Aktiva": "Jml Aktiva", "Jumlah1": total_aktiva, "Passiva": "Jml Kewajiban & Ekuitas", "Jumlah2": total_passiva})
            
            df_neraca_lap = pd.DataFrame(neraca_data)
            
            st.dataframe(
                df_neraca_lap.style.format({
                    "Jumlah1": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x,
                    "Jumlah2": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
                })
                .apply(lambda x: ['font-weight: bold' if 'Jml' in str(df_neraca_lap.loc[i, 'Aktiva']) or 'Jml' in str(df_neraca_lap.loc[i, 'Passiva']) else '' for i in range(len(x))], axis=0)
                .set_properties(**{'text-align': 'left'}, subset=['Aktiva', 'Passiva'])
                .set_properties(**{'text-align': 'right'}, subset=['Jumlah1', 'Jumlah2']),
                use_container_width=True,
                hide_index=True
            )
            
            # Validasi Balance
            if abs(total_aktiva - total_passiva) < 0.01:
                st.success(f"✅ Neraca BALANCE! Total: Rp {format_rupiah(total_aktiva)}")
            else:
                st.error(f"❌ Neraca TIDAK BALANCE! Aktiva: Rp {format_rupiah(total_aktiva)} vs Passiva: Rp {format_rupiah(total_passiva)}")
            
            # PDF Export Neraca
            def buat_pdf_neraca_lap(df, bulan, tahun):
                pdf = FPDF()
                pdf.add_page()
                
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, txt="Laporan Neraca", ln=True, align="C")
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 8, txt="BUMDes", ln=True, align="C")
                pdf.cell(0, 8, txt=f"Periode: {bulan_dict[bulan]} {tahun}", ln=True, align="C")
                pdf.ln(5)

                pdf.set_font("Arial", 'B', 10)
                col_widths = [60, 30, 60, 30]
                headers = ["Aktiva", "Jumlah (Rp)", "Passiva", "Jumlah (Rp)"]
                
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, border=1, align="C")
                pdf.ln()

                pdf.set_font("Arial", '', 9)
                for _, row in df.iterrows():
                    is_bold = 'Jml' in str(row['Aktiva']) or 'Jml' in str(row['Passiva'])
                    if is_bold:
                        pdf.set_font("Arial", 'B', 9)
                    
                    pdf.cell(col_widths[0], 8, str(row["Aktiva"]), border=1, align="L")
                    
                    jumlah1_text = format_rupiah(row["Jumlah1"]) if isinstance(row["Jumlah1"], (int, float)) else ""
                    pdf.cell(col_widths[1], 8, jumlah1_text, border=1, align="R")
                    
                    pdf.cell(col_widths[2], 8, str(row["Passiva"]), border=1, align="L")
                    
                    jumlah2_text = format_rupiah(row["Jumlah2"]) if isinstance(row["Jumlah2"], (int, float)) else ""
                    pdf.cell(col_widths[3], 8, jumlah2_text, border=1, align="R")
                    
                    pdf.ln()
                    
                    if is_bold:
                        pdf.set_font("Arial", '', 9)

                pdf.ln(5)
                pdf.set_font("Arial", 'I', 8)
                pdf.cell(0, 5, txt="Dicetak dari Sistem Akuntansi BUMDes", ln=True, align="C")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    pdf.output(tmp.name)
                    tmp.seek(0)
                    return tmp.read()

            pdf_neraca_lap = buat_pdf_neraca_lap(df_neraca_lap, bulan_laporan, tahun_laporan)
            st.download_button(
                "📥 Download PDF Neraca",
                data=pdf_neraca_lap,
                file_name=f"laporan_neraca_{bulan_laporan}_{tahun_laporan}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # ========================================
        # SUB-TAB 3: LAPORAN ARUS KAS
        # ========================================
        with subtab3:
            st.markdown("### 💸 Laporan Arus Kas")
            st.markdown(f"**BUMDes - {bulan_dict[bulan_laporan]} {tahun_laporan}**")
            st.markdown("---")
            
            # Input manual untuk Arus Kas (karena tidak bisa auto-generate)
            st.info("💡 Laporan Arus Kas memerlukan input manual karena tidak bisa digenerate otomatis dari Neraca Saldo.")
            
            if "arus_kas_refresh" not in st.session_state:
                st.session_state.arus_kas_refresh = 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("#### Arus Kas Operasi:")
                if st.button("➕ Tambah Operasi", key="tambah_operasi"):
                    new_row = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                    st.session_state.arus_kas_operasi = pd.concat([st.session_state.arus_kas_operasi, new_row], ignore_index=True)
                    st.session_state.arus_kas_refresh += 1
                    st.rerun()
                
                new_arus_operasi = create_aggrid(st.session_state.arus_kas_operasi, f"operasi_{st.session_state.arus_kas_refresh}", height=250)
                if not new_arus_operasi.equals(st.session_state.arus_kas_operasi):
                    st.session_state.arus_kas_operasi = new_arus_operasi.copy()

            with col2:
                st.write("#### Arus Kas Investasi:")
                if st.button("➕ Tambah Investasi", key="tambah_investasi"):
                    new_row = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                    st.session_state.arus_kas_investasi = pd.concat([st.session_state.arus_kas_investasi, new_row], ignore_index=True)
                    st.session_state.arus_kas_refresh += 1
                    st.rerun()
                
                new_arus_investasi = create_aggrid(st.session_state.arus_kas_investasi, f"investasi_{st.session_state.arus_kas_refresh}", height=250)
                if not new_arus_investasi.equals(st.session_state.arus_kas_investasi):
                    st.session_state.arus_kas_investasi = new_arus_investasi.copy()

            with col3:
                st.write("#### Arus Kas Pendanaan:")
                if st.button("➕ Tambah Pendanaan", key="tambah_pendanaan"):
                    new_row = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                    st.session_state.arus_kas_pendanaan = pd.concat([st.session_state.arus_kas_pendanaan, new_row], ignore_index=True)
                    st.session_state.arus_kas_refresh += 1
                    st.rerun()
                
                new_arus_pendanaan = create_aggrid(st.session_state.arus_kas_pendanaan, f"pendanaan_{st.session_state.arus_kas_refresh}", height=250)
                if not new_arus_pendanaan.equals(st.session_state.arus_kas_pendanaan):
                    st.session_state.arus_kas_pendanaan = new_arus_pendanaan.copy()

            # Tombol kontrol untuk Arus Kas
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Hapus Kosong Operasi", key="hapus_operasi_kosong"):
                    st.session_state.arus_kas_operasi = st.session_state.arus_kas_operasi[
                        st.session_state.arus_kas_operasi["Aktivitas"].astype(str).str.strip() != ""
                    ].reset_index(drop=True)
                    if len(st.session_state.arus_kas_operasi) == 0:
                        st.session_state.arus_kas_operasi = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                    st.session_state.arus_kas_refresh += 1
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Hapus Kosong Investasi", key="hapus_investasi_kosong"):
                    st.session_state.arus_kas_investasi = st.session_state.arus_kas_investasi[
                        st.session_state.arus_kas_investasi["Aktivitas"].astype(str).str.strip() != ""
                    ].reset_index(drop=True)
                    if len(st.session_state.arus_kas_investasi) == 0:
                        st.session_state.arus_kas_investasi = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                    st.session_state.arus_kas_refresh += 1
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Hapus Kosong Pendanaan", key="hapus_pendanaan_kosong"):
                    st.session_state.arus_kas_pendanaan = st.session_state.arus_kas_pendanaan[
                        st.session_state.arus_kas_pendanaan["Aktivitas"].astype(str).str.strip() != ""
                    ].reset_index(drop=True)
                    if len(st.session_state.arus_kas_pendanaan) == 0:
                        st.session_state.arus_kas_pendanaan = pd.DataFrame([{"Aktivitas": "", "Jumlah (Rp)": 0}])
                    st.session_state.arus_kas_refresh += 1
                    st.rerun()

            st.markdown("---")

            df_operasi_clean = new_arus_operasi[new_arus_operasi["Aktivitas"].astype(str).str.strip() != ""]
            df_investasi_clean = new_arus_investasi[new_arus_investasi["Aktivitas"].astype(str).str.strip() != ""]
            df_pendanaan_clean = new_arus_pendanaan[new_arus_pendanaan["Aktivitas"].astype(str).str.strip() != ""]

            if not df_operasi_clean.empty or not df_investasi_clean.empty or not df_pendanaan_clean.empty:
                st.write("### 📊 Hasil Laporan Arus Kas")
                
                # Format data untuk tabel
                arus_kas_data = []
                arus_kas_data.append({"Aktivitas": "Arus Kas Operasi:", "Jumlah": ""})
                
                for _, row in df_operasi_clean.iterrows():
                    arus_kas_data.append({"Aktivitas": f"  {row['Aktivitas']}", "Jumlah": row["Jumlah (Rp)"]})
                
                arus_kas_data.append({"Aktivitas": "", "Jumlah": ""})
                arus_kas_data.append({"Aktivitas": "Arus Kas Investasi:", "Jumlah": ""})
                
                for _, row in df_investasi_clean.iterrows():
                    arus_kas_data.append({"Aktivitas": f"  {row['Aktivitas']}", "Jumlah": row["Jumlah (Rp)"]})
                
                arus_kas_data.append({"Aktivitas": "", "Jumlah": ""})
                arus_kas_data.append({"Aktivitas": "Arus Kas Pendanaan:", "Jumlah": ""})
                
                for _, row in df_pendanaan_clean.iterrows():
                    arus_kas_data.append({"Aktivitas": f"  {row['Aktivitas']}", "Jumlah": row["Jumlah (Rp)"]})

                df_arus_kas = pd.DataFrame(arus_kas_data)

                st.dataframe(
                    df_arus_kas.style.format({
                        "Jumlah": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
                    })
                    .apply(lambda x: ['font-weight: bold' if 'Arus Kas' in str(df_arus_kas.loc[i, 'Aktivitas']) else '' for i in range(len(x))], axis=0)
                    .set_properties(**{'text-align': 'left'}, subset=['Aktivitas'])
                    .set_properties(**{'text-align': 'right'}, subset=['Jumlah']),
                    use_container_width=True,
                    hide_index=True
                )
                
                # PDF Export Arus Kas
                def buat_pdf_arus_kas(df, bulan, tahun):
                    pdf = FPDF()
                    pdf.add_page()
                    
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, txt="Laporan Arus Kas", ln=True, align="C")
                    pdf.set_font("Arial", '', 12)
                    pdf.cell(0, 8, txt="BUMDes", ln=True, align="C")
                    pdf.cell(0, 8, txt=f"Periode: {bulan_dict[bulan]} {tahun}", ln=True, align="C")
                    pdf.ln(5)

                    pdf.set_font("Arial", 'B', 10)
                    col_widths = [120, 60]
                    headers = ["Aktivitas", "Jumlah (Rp)"]
                    
                    for i, header in enumerate(headers):
                        pdf.cell(col_widths[i], 10, header, border=1, align="C")
                    pdf.ln()

                    pdf.set_font("Arial", '', 9)
                    for _, row in df.iterrows():
                        is_bold = 'Arus Kas' in str(row['Aktivitas'])
                        if is_bold:
                            pdf.set_font("Arial", 'B', 9)
                        
                        aktivitas = str(row["Aktivitas"])
                        if len(aktivitas) > 50:
                            aktivitas = aktivitas[:47] + "..."
                        pdf.cell(col_widths[0], 8, aktivitas, border=1, align="L")
                        
                        jumlah_text = format_rupiah(row["Jumlah"]) if isinstance(row["Jumlah"], (int, float)) else ""
                        pdf.cell(col_widths[1], 8, jumlah_text, border=1, align="R")
                        pdf.ln()
                        
                        if is_bold:
                            pdf.set_font("Arial", '', 9)

                    pdf.ln(5)
                    pdf.set_font("Arial", 'I', 8)
                    pdf.cell(0, 5, txt="Dicetak dari Sistem Akuntansi BUMDes", ln=True, align="C")

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        pdf.output(tmp.name)
                        tmp.seek(0)
                        return tmp.read()

                pdf_arus_kas = buat_pdf_arus_kas(df_arus_kas, bulan_laporan, tahun_laporan)
                st.download_button(
                    "📥 Download PDF Arus Kas",
                    data=pdf_arus_kas,
                    file_name=f"laporan_arus_kas_{bulan_laporan}_{tahun_laporan}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ Belum ada data untuk Laporan Arus Kas. Silakan isi data terlebih dahulu.")
