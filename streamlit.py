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

# === Fungsi format rupiah ===
def format_rupiah(x):
    try:
        if x < 0:
            return f"(Rp {abs(x):,.0f})".replace(",", ".")
        return f"Rp {x:,.0f}".replace(",", ".")
    except Exception:
        return x

# === Styling agar mirip Streamlit ===
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
    st.info("💡 Tekan Enter sekali untuk menyimpan perubahan otomatis, seperti di tabel Streamlit.")

    # === Setup Grid AgGrid ===
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
        key="aggrid_table"
    )

    # === Sinkronisasi otomatis ===
    new_df = pd.DataFrame(grid_response["data"])
    if not new_df.equals(st.session_state.data):
        st.session_state.data = new_df.copy()
        st.toast("💾 Perubahan tersimpan otomatis!", icon="💾")

    # === Bersihkan data kosong ===
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

        # === Fungsi buat PDF ===
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
    st.subheader("Periode Januari 2025")

    # Data Dummy Neraca Saldo (akan diambil dari Buku Besar nantinya)
    data_neraca_saldo = [
        {"No Akun": "101", "Nama Akun": "Kas", "Debit (Rp)": 12_200_000, "Kredit (Rp)": 0},
        {"No Akun": "102", "Nama Akun": "Peralatan", "Debit (Rp)": 8_000_000, "Kredit (Rp)": 0},
        {"No Akun": "103", "Nama Akun": "Perlengkapan", "Debit (Rp)": 1_500_000, "Kredit (Rp)": 0},
        {"No Akun": "501", "Nama Akun": "Beban sewa", "Debit (Rp)": 1_000_000, "Kredit (Rp)": 0},
        {"No Akun": "502", "Nama Akun": "Beban BBM", "Debit (Rp)": 600_000, "Kredit (Rp)": 0},
        {"No Akun": "503", "Nama Akun": "Beban gaji", "Debit (Rp)": 2_500_000, "Kredit (Rp)": 0},
        {"No Akun": "504", "Nama Akun": "Beban listrik", "Debit (Rp)": 400_000, "Kredit (Rp)": 0},
        {"No Akun": "505", "Nama Akun": "Beban perawatan", "Debit (Rp)": 300_000, "Kredit (Rp)": 0},
        {"No Akun": "301", "Nama Akun": "Modal", "Debit (Rp)": 0, "Kredit (Rp)": 20_000_000},
        {"No Akun": "401", "Nama Akun": "Pendapatan", "Debit (Rp)": 0, "Kredit (Rp)": 7_500_000},
        {"No Akun": "302", "Nama Akun": "Prive", "Debit (Rp)": 1_000_000, "Kredit (Rp)": 0},
    ]

    df_neraca = pd.DataFrame(data_neraca_saldo)

    # Hitung total
    total_debit = df_neraca["Debit (Rp)"].sum()
    total_kredit = df_neraca["Kredit (Rp)"].sum()

    # Tambahkan baris total
    df_total = pd.DataFrame({
        "No Akun": [""],
        "Nama Akun": ["Jumlah"],
        "Debit (Rp)": [total_debit],
        "Kredit (Rp)": [total_kredit]
    })

    df_neraca_final = pd.concat([df_neraca, df_total], ignore_index=True)
    df_neraca_final.index = range(1, len(df_neraca_final) + 1)
    df_neraca_final.index.name = "No"

    # Tampilkan tabel
    st.dataframe(
        df_neraca_final.style.format({
            "Debit (Rp)": format_rupiah,
            "Kredit (Rp)": format_rupiah,
        }).apply(lambda x: ['font-weight: bold' if i == len(df_neraca_final) else '' for i in range(len(x))], axis=0),
        use_container_width=True
    )

    # Validasi Balance
    if total_debit == total_kredit:
        st.success(f"✅ Neraca Saldo BALANCE! Total: {format_rupiah(total_debit)}")
    else:
        st.error(f"❌ Neraca Saldo TIDAK BALANCE! Debit: {format_rupiah(total_debit)} vs Kredit: {format_rupiah(total_kredit)}")

# ========================================
# TAB 4: LAPORAN KEUANGAN
# ========================================
with tab4:
    st.header("📊 Laporan Keuangan BUMDes")
    st.subheader("Periode Januari 2025")

    # Data dari Neraca Saldo (simulasi)
    data_ref = {
        "kas": 12_200_000,
        "perlengkapan": 1_500_000,
        "peralatan": 8_000_000,
        "modal_awal": 20_000_000,
        "prive": 1_000_000,
        "pendapatan_sampah": 4_000_000,
        "pendapatan_olahan": 3_500_000,
        "beban_sewa": 1_000_000,
        "beban_gaji": 2_500_000,
        "beban_operasional": 600_000,
        "beban_listrik": 400_000,
        "beban_perawatan": 300_000,
    }

    # ========================================
    # 1. LAPORAN LABA/RUGI
    # ========================================
    st.markdown("---")
    st.markdown("### 📈 Laporan Laba/Rugi")

    total_pendapatan = data_ref["pendapatan_sampah"] + data_ref["pendapatan_olahan"]
    total_beban = (data_ref["beban_sewa"] + data_ref["beban_gaji"] + 
                   data_ref["beban_operasional"] + data_ref["beban_listrik"] + 
                   data_ref["beban_perawatan"])
    laba_bersih = total_pendapatan - total_beban

    df_labarugi = pd.DataFrame([
        {"Keterangan": "Pendapatan:", "Jumlah (Rp)": ""},
        {"Keterangan": "  1. Pendapatan pengumpulan sampah", "Jumlah (Rp)": data_ref["pendapatan_sampah"]},
        {"Keterangan": "  2. Penjualan olahan sampah/kompos", "Jumlah (Rp)": data_ref["pendapatan_olahan"]},
        {"Keterangan": "", "Jumlah (Rp)": ""},
        {"Keterangan": "Total Pendapatan", "Jumlah (Rp)": total_pendapatan},
        {"Keterangan": "", "Jumlah (Rp)": ""},
        {"Keterangan": "Beban-Beban:", "Jumlah (Rp)": ""},
        {"Keterangan": "  1. Sewa lahan", "Jumlah (Rp)": data_ref["beban_sewa"]},
        {"Keterangan": "  2. Gaji Pegawai", "Jumlah (Rp)": data_ref["beban_gaji"]},
        {"Keterangan": "  3. Operasional kendaraan", "Jumlah (Rp)": data_ref["beban_operasional"]},
        {"Keterangan": "  4. Listrik dan air", "Jumlah (Rp)": data_ref["beban_listrik"]},
        {"Keterangan": "  5. Perawatan alat", "Jumlah (Rp)": data_ref["beban_perawatan"]},
        {"Keterangan": "", "Jumlah (Rp)": ""},
        {"Keterangan": "Total Beban", "Jumlah (Rp)": total_beban},
        {"Keterangan": "", "Jumlah (Rp)": ""},
        {"Keterangan": "Laba Bersih", "Jumlah (Rp)": laba_bersih},
    ])

    st.dataframe(
        df_labarugi.style.format({"Jumlah (Rp)": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x})
        .apply(lambda x: ['font-weight: bold' if i in [4, 13, 15] else '' for i in range(len(x))], axis=0)
        .set_properties(**{'text-align': 'left'}, subset=['Keterangan'])
        .set_properties(**{'text-align': 'right'}, subset=['Jumlah (Rp)']),
        use_container_width=True,
        hide_index=True
    )

    # ========================================
    # 2. LAPORAN PERUBAHAN MODAL
    # ========================================
    st.markdown("---")
    st.markdown("### 💰 Laporan Perubahan Modal")

    modal_akhir = data_ref["modal_awal"] + laba_bersih - data_ref["prive"]

    df_modal = pd.DataFrame([
        {"Keterangan": "Modal Awal", "Jumlah (Rp)": data_ref["modal_awal"]},
        {"Keterangan": "Laba Bersih", "Jumlah (Rp)": laba_bersih},
        {"Keterangan": "Prive", "Jumlah (Rp)": data_ref["prive"]},
        {"Keterangan": "", "Jumlah (Rp)": ""},
        {"Keterangan": "Modal Akhir", "Jumlah (Rp)": modal_akhir},
    ])

    st.dataframe(
        df_modal.style.format({"Jumlah (Rp)": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x})
        .apply(lambda x: ['font-weight: bold' if i == 4 else '' for i in range(len(x))], axis=0)
        .set_properties(**{'text-align': 'left'}, subset=['Keterangan'])
        .set_properties(**{'text-align': 'right'}, subset=['Jumlah (Rp)']),
        use_container_width=True,
        hide_index=True
    )

    # ========================================
    # 3. LAPORAN NERACA
    # ========================================
    st.markdown("---")
    st.markdown("### 🏦 Laporan Neraca (Posisi Keuangan)")

    jml_aktiva_lancar = data_ref["kas"] + data_ref["perlengkapan"]
    jml_aktiva = jml_aktiva_lancar + data_ref["peralatan"]
    jml_kewajiban_ekuitas = modal_akhir

    df_neraca_lap = pd.DataFrame([
        {"Aktiva": "Aktiva Lancar:", "Jumlah (Rp)": "", "Passiva": "Kewajiban:", "Jumlah2 (Rp)": ""},
        {"Aktiva": "  Kas", "Jumlah (Rp)": data_ref["kas"], "Passiva": "  Hutang usaha", "Jumlah2 (Rp)": 0},
        {"Aktiva": "  Perlengkapan", "Jumlah (Rp)": data_ref["perlengkapan"], "Passiva": "  Hutang air listrik", "Jumlah2 (Rp)": 0},
        {"Aktiva": "", "Jumlah (Rp)": "", "Passiva": "  Hutang Bank", "Jumlah2 (Rp)": 0},
        {"Aktiva": "", "Jumlah (Rp)": "", "Passiva": "", "Jumlah2 (Rp)": ""},
        {"Aktiva": "Jml aktiva lancar", "Jumlah (Rp)": jml_aktiva_lancar, "Passiva": "Ekuitas:", "Jumlah2 (Rp)": ""},
        {"Aktiva": "", "Jumlah (Rp)": "", "Passiva": "  Modal", "Jumlah2 (Rp)": data_ref["modal_awal"]},
        {"Aktiva": "Aktiva Tetap:", "Jumlah (Rp)": "", "Passiva": "  Laba", "Jumlah2 (Rp)": laba_bersih},
        {"Aktiva": "  Peralatan", "Jumlah (Rp)": data_ref["peralatan"], "Passiva": "  Prive", "Jumlah2 (Rp)": -data_ref["prive"]},
        {"Aktiva": "  Akumulasi Penyusutan Peralatan", "Jumlah (Rp)": 0, "Passiva": "", "Jumlah2 (Rp)": ""},
        {"Aktiva": "", "Jumlah (Rp)": "", "Passiva": "", "Jumlah2 (Rp)": ""},
        {"Aktiva": "Jml Aktiva", "Jumlah (Rp)": jml_aktiva, "Passiva": "Jml Kewajiban&Ekuitas", "Jumlah2 (Rp)": jml_kewajiban_ekuitas},
    ])

    st.dataframe(
        df_neraca_lap.style.format({
            "Jumlah (Rp)": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x,
            "Jumlah2 (Rp)": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
        })
        .apply(lambda x: ['font-weight: bold' if i in [5, 11] else '' for i in range(len(x))], axis=0)
        .set_properties(**{'text-align': 'left'}, subset=['Aktiva', 'Passiva'])
        .set_properties(**{'text-align': 'right'}, subset=['Jumlah (Rp)', 'Jumlah2 (Rp)']),
        use_container_width=True,
        hide_index=True
    )

    # Validasi Balance
    if jml_aktiva == jml_kewajiban_ekuitas:
        st.success(f"✅ Neraca BALANCE! Total: {format_rupiah(jml_aktiva)}")
    else:
        st.error(f"❌ Neraca TIDAK BALANCE! Aktiva: {format_rupiah(jml_aktiva)} vs Passiva: {format_rupiah(jml_kewajiban_ekuitas)}")

    # ========================================
    # 4. LAPORAN ARUS KAS
    # ========================================
    st.markdown("---")
    st.markdown("### 💸 Laporan Arus Kas")

    df_arus_kas = pd.DataFrame([
        {"Aktivitas": "Arus Kas Operasi:", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": ""},
        {"Aktivitas": "  Penerimaan pengumpulan sampah", "Kas Masuk (Rp)": data_ref["pendapatan_sampah"], "Kas Keluar (Rp)": ""},
        {"Aktivitas": "  Penerimaan penjualan daur ulang", "Kas Masuk (Rp)": data_ref["pendapatan_olahan"], "Kas Keluar (Rp)": ""},
        {"Aktivitas": "  Pembayaran sewa lahan", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["beban_sewa"]},
        {"Aktivitas": "  Pembayaran Gaji", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["beban_gaji"]},
        {"Aktivitas": "  Pembayaran BBM", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["beban_operasional"]},
        {"Aktivitas": "  Pembayaran Listrik & air", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["beban_listrik"]},
        {"Aktivitas": "  Pembayaran Perawatan", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["beban_perawatan"]},
        {"Aktivitas": "", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": ""},
        {"Aktivitas": "Arus Kas Investasi:", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": ""},
        {"Aktivitas": "  Pembelian peralatan", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["peralatan"]},
        {"Aktivitas": "  Pembelian perlengkapan", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["perlengkapan"]},
        {"Aktivitas": "", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": ""},
        {"Aktivitas": "Arus Kas Pendanaan:", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": ""},
        {"Aktivitas": "  Setoran modal", "Kas Masuk (Rp)": data_ref["modal_awal"], "Kas Keluar (Rp)": ""},
        {"Aktivitas": "  Prive", "Kas Masuk (Rp)": "", "Kas Keluar (Rp)": data_ref["prive"]},
    ])

    st.dataframe(
        df_arus_kas.style.format({
            "Kas Masuk (Rp)": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x,
            "Kas Keluar (Rp)": lambda x: format_rupiah(x) if isinstance(x, (int, float)) else x
        })
        .apply(lambda x: ['font-weight: bold' if i in [0, 9, 13] else '' for i in range(len(x))], axis=0)
        .set_properties(**{'text-align': 'left'}, subset=['Aktivitas'])
        .set_properties(**{'text-align': 'right'}, subset=['Kas Masuk (Rp)', 'Kas Keluar (Rp)']),
        use_container_width=True,
        hide_index=True
    )

    st.info("💡 Laporan Arus Kas menampilkan aliran kas berdasarkan aktivitas operasi, investasi, dan pendanaan.")
