import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Faker ve Random ayarları
fake = Faker('tr_TR')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Excel'i oku
df_pos = pd.read_excel('job_architecture.xlsx', sheet_name='Pozisyon Listesi')
positions = df_pos.to_dict('records')

# Departman Ağırlıklarını Ayarlama (3 Üretim Tesisi Simülasyonu)
dept_weights = []
for pos in positions:
    dept = pos['Departman']
    if dept == 'Production':
        dept_weights.append(50)  # Üretim sayısını devasa yapıyoruz
    elif dept in ['Sales', 'Supply Chain']:
        dept_weights.append(20)  # Satış ve Lojistik de yüksek
    elif dept == 'Human Resources':
        dept_weights.append(2)   # İK sayısını baskılıyoruz
    else:
        dept_weights.append(5)   # Diğer departmanlar standart

NUM_ROWS = 4000  # İstediğin gibi 4000 satır
countries = ['Turkey', 'Türkiye', 'UK', 'USA']
locations = ['Istanbul', 'Sütlüce', 'Gebze', 'Çayırova', 'Bolu']
genders = ['Male', 'Female', 'M', 'F', 'm', 'f', 'MALE', 'FEMALE', 'Erkek', 'Kadın']
worker_types = ['Employee', 'Contingent Worker', 'Contractor']

# ---------------------------------------------------------------------------------
# BÖLÜM 1: TÜM ÇALIŞANLARIN TEMEL ÖZELLİKLERİNİ VE RİSK SKORLARINI ÜRETME
# ---------------------------------------------------------------------------------
temp_employees = []
churn_scores = []

for i in range(NUM_ROWS):
    emp_id = 10000 + i
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}".lower()

    hire_date = fake.date_between(start_date='-10y', end_date='today')
    dob = fake.date_of_birth(minimum_age=18, maximum_age=65)

    pos_info = random.choices(positions, weights=dept_weights, k=1)[0]
    department = pos_info['Departman']

    if department == 'Human Resources' and random.random() < 0.20:
        department_name = 'EHS & Adminastrative Affairs'
    else:
        department_name = department

    job_title = pos_info['Pozisyon'].lower()
    grade = pos_info['Grade']
    manager_title = pos_info['Bağlı Olduğu Pozisyon']
    min_salary = pos_info['Min Brüt Maaş (₺)']
    max_salary = pos_info['Maks Brüt Maaş (₺)']

    base_salary = fake.random_int(min=min_salary, max=max_salary)
    grade_midpoint = (min_salary + max_salary) / 2
    compa_ratio = round(base_salary / grade_midpoint, 2)

    car_allowance = fake.random_int(min=2000, max=10000) if grade <= 5 else 0
    sports_allowance = fake.random_int(min=500, max=1500)
    transport_allowance = fake.random_int(min=1000, max=3000)

    last_promo_years = round(random.uniform(0.5, 6.0), 1)
    years_in_pos = round(random.uniform(0.1, 5.0), 1)
    age = (datetime.now().date() - dob).days // 365
    is_manager = 'Yes' if pos_info['Kariyer Track'] == 'Manager' else 'No'

    # --- ML İÇİN SİHİRLİ KISIM: KORELASYON SKORU ---
    # Herkesin baz bir ayrılma puanı var (Örn: 10). Sorunu olanların puanı fırlıyor.
    score = 10
    if compa_ratio < 0.85: score += 60        # Maaşı düşük olanın riski devasa artar
    if last_promo_years > 3.5: score += 40    # Terfi alamayanın riski çok artar
    if years_in_pos > 4.0: score += 30        # Pozisyonda sıkılanın riski artar
    if age > 56: score += 30                  # Emekliliği gelenin riski artar
    if is_manager == 'No' and grade >= 8: score += 15 # Düşük seviye personelin sirkülasyonu fazladır

    emp_dict = {
        "Employee ID": emp_id, "Full Legal Name": full_name, "Hire Date": hire_date, "Date of Birth": dob,
        "Age": age, "Gender": random.choice(genders), "Business Unit": department_name,
        "Job Title": job_title, "Base Salary": base_salary, "Compa-Ratio": compa_ratio,
        "Last Promotion Years Ago": last_promo_years, "Years in Current Position": years_in_pos,
        "Is Manager": is_manager, "Levels from Top of Organisation (CEO=2)": grade,
        "Manager's Business Title": manager_title, "Car Allowance": car_allowance,
        "Sports Allowance": sports_allowance, "Transportation Allowance": transport_allowance,
        "Worker Type": random.choice(worker_types), "Country": random.choice(countries),
        "Location": random.choice(locations), "Number of Direct Reports": random.randint(0, 10) if is_manager == 'Yes' else 0
    }
    temp_employees.append(emp_dict)
    churn_scores.append(score)

# ---------------------------------------------------------------------------------
# BÖLÜM 2: SKORLARA (KORELASYONA) GÖRE HEDEFLERİ BELİRLEME
# ---------------------------------------------------------------------------------
n_terminated = int(NUM_ROWS * 0.40)

# Skorları olasılığa (probability) çevirip, yüksek skorluları ağırlıklı olarak seçiyoruz
churn_probs = np.array(churn_scores) / sum(churn_scores)
terminated_indices = np.random.choice(range(NUM_ROWS), size=n_terminated, replace=False, p=churn_probs)
terminated_set = set(terminated_indices)
active_indices = list(set(range(NUM_ROWS)) - terminated_set)

# İzin Dağılımları (Sadece aktif çalışanlar izne çıkabilir)
on_leave_indices = set(random.sample(active_indices, int(NUM_ROWS * 0.20)))
on_leave_list = list(on_leave_indices)
maternity_indices = set(on_leave_list[:int(len(on_leave_list)*0.03)])
military_indices = set(on_leave_list[int(len(on_leave_list)*0.03):int(len(on_leave_list)*0.05)])
sick_indices = set(on_leave_list[int(len(on_leave_list)*0.05):int(len(on_leave_list)*0.15)])

# ---------------------------------------------------------------------------------
# BÖLÜM 3: NİHAİ VERİYİ BİRLEŞTİRME VE MANTIKLI SEBEP (REASON) ATAMASI
# ---------------------------------------------------------------------------------
final_data = []

for i, emp in enumerate(temp_employees):
    # STATUS & TERMINATION REASON MANTIĞI
    if i in terminated_set:
        emp['Status'] = 'Terminated'
        emp['End Employment Date'] = fake.date_between(start_date=emp['Hire Date'], end_date='today')

        # Ayrılan kişinin sebebini, o kişinin profilindeki GERÇEK soruna göre atıyoruz (Makine Öğrenmesi bunu yakalayacak)
        if emp['Compa-Ratio'] < 0.85 and random.random() < 0.7:
            emp['Termination Reason'] = 'Pay Dissatisfaction'
        elif emp['Last Promotion Years Ago'] > 3.5 and random.random() < 0.7:
            emp['Termination Reason'] = 'Lack of Promotion'
        elif emp['Age'] > 56 and random.random() < 0.8:
            emp['Termination Reason'] = 'Retirement'
        elif emp['Years in Current Position'] > 4.0 and random.random() < 0.6:
            emp['Termination Reason'] = 'Career Development'
        else:
            other_reasons = ['Personal Reasons', 'Relocation', 'Work-Life Balance / Burnout', 'Health Reasons']
            emp['Termination Reason'] = random.choices(other_reasons, weights=[0.40, 0.20, 0.30, 0.10], k=1)[0]
    else:
        emp['Status'] = 'Active'
        emp['End Employment Date'] = np.nan
        emp['Termination Reason'] = np.nan

    # LEAVE (İzin) MANTIĞI
    if i in on_leave_indices:
        emp['Leave Status'] = "On Leave"
        if i in maternity_indices:
            emp['Leave Type'] = "Maternity Leave"
            emp['Gender'] = random.choice(['Female', 'F', 'f', 'FEMALE', 'Kadın']) # Doğum izni cinsiyet kontrolü
        elif i in military_indices:
            emp['Leave Type'] = "Military Leave"
            emp['Gender'] = random.choice(['Male', 'M', 'm', 'MALE', 'Erkek']) # Askerlik cinsiyet kontrolü
        elif i in sick_indices:
            emp['Leave Type'] = "Sick Leave"
        else:
            emp['Leave Type'] = "Annual Leave"
    else:
        emp['Leave Status'] = "Not on Leave"
        emp['Leave Type'] = np.nan

    # Eksik Kalan Statik Sütunları Tamamlama
    emp["MUD ID"] = f"MUD{emp['Employee ID']}"
    emp["Email - Work"] = f"{emp['Full Legal Name'].split()[0]}.{emp['Full Legal Name'].split()[-1]}@beko.com"
    emp["Position ID"] = f"POS-{fake.random_int(min=100, max=999)}"
    emp["Position"] = emp["Job Title"]
    emp["Effective Date for Current Position"] = emp["Hire Date"] + timedelta(days=random.randint(0, 365))
    emp["Business Title"] = emp["Job Title"]
    emp["Employee\ CW Type"] = "Regular"
    emp["Is International Assignee"] = random.choice(['Yes', 'No'])
    emp["Scheduled Weekly Hours"] = random.choice([40, 45, np.nan, 80])
    emp["Default Weekly Hours"] = 45
    emp["FTE %"] = random.choice([100, 50, 0])
    emp["Work Shift"] = "Day"
    emp["Company Code"] = "BEKO01"
    emp["Company"] = "Beko"
    emp["Sub-function"] = "Operations"
    emp["Supervisory Organization"] = f"{emp['Business Unit']} Org"
    emp["Supervisory Org ID"] = f"ORG-{fake.random_int(min=100, max=199)}"
    emp["Region"] = "EMEA"
    emp["Cost Center - ID"] = fake.random_int(min=1000, max=9999)
    emp["Cost Center - Name"] = f"CC-{emp['Business Unit']}"
    emp["Cost Center Hierarchy"] = "Global -> EMEA"
    emp["Job Category"] = "Professional"
    emp["Job Family Group"] = "Corporate"
    emp["Job Family"] = emp['Business Unit']
    emp["Job Profile"] = emp["Job Title"]
    emp["Job Code"] = f"JC-{emp['Levels from Top of Organisation (CEO=2)']}-{fake.random_int(min=10, max=99)}"
    emp["Company Service Date"] = emp["Hire Date"]
    emp["Original Hire Date"] = emp["Hire Date"]
    emp["Is Rehire"] = "No"
    emp["Continuous Service Date"] = emp["Hire Date"]
    emp["Years - Continuous Service Date"] = round(random.uniform(0.1, 10), 1)
    emp["Months - Continuous Service Date"] = random.randint(1, 120)
    emp["Contract Start Date"] = emp["Hire Date"]
    emp["Start Date (Remotely)"] = np.nan
    emp["Date of Move"] = np.nan
    emp["Clawback End Date"] = np.nan
    emp["Assignment End Date"] = np.nan
    emp["Mobility Support Type"] = np.nan
    emp["Manager's MUD ID"] = "MUD9999"
    emp["Manager's Employee ID"] = "9999"
    emp["Worker's Manager"] = emp["Manager's Business Title"]
    emp["Manager's Supervisory Organisation"] = f"{emp['Business Unit']} Org"
    emp["Manager's Email"] = "manager@beko.com"
    emp["Manager's Country"] = "Turkey"
    emp["Manager's Location"] = "Istanbul"
    emp["Country of Birth"] = random.choice(countries)
    emp["City of Birth"] = fake.city()
    emp["Home Phones"] = fake.phone_number()
    emp["Payroll ID"] = f"PAY-{emp['Employee ID']}"
    emp["Legacy ID"] = np.nan
    emp["Pay Group"] = "Monthly"
    emp["CEO"] = "Hakan Bulgurlu"
    emp["CEO Business Title"] = "CEO"

    # Boş CET Sütunları
    for col in ["CET", "CET Business Title", "CET-1", "CET-1 Business Title", "CET-2", "CET-2 Business Title",
                "CET-3", "CET-3 Business Title", "CET-4", "CET-4 Business Title", "CET-5", "CET-5 Business Title",
                "CET-6", "CET-6 Business Title", "Management Levels (Benefit Jobs)"]:
        emp[col] = np.nan

    final_data.append(emp)

df = pd.DataFrame(final_data)

# Sütun sırasını orijinal formata oturtma (Temizlik aşaması için)
cols = ["Employee ID", "Full Legal Name", "Status", "Leave Status", "Leave Type", "Termination Reason", "Compa-Ratio",
        "Last Promotion Years Ago", "MUD ID", "Email - Work", "Position ID", "Position", "Effective Date for Current Position",
        "Years in Current Position", "Business Title", "Job Title", "Worker Type", "Employee\ CW Type", "Is International Assignee",
        "Is Manager", "Scheduled Weekly Hours", "Default Weekly Hours", "FTE %", "Work Shift", "Country", "Company Code",
        "Company", "Location", "Business Unit", "Sub-function", "Supervisory Organization", "Supervisory Org ID", "Region",
        "Cost Center - ID", "Cost Center - Name", "Cost Center Hierarchy", "Job Category", "Job Family Group", "Job Family",
        "Job Profile", "Job Code", "End Employment Date", "Company Service Date", "Original Hire Date", "Hire Date", "Is Rehire",
        "Continuous Service Date", "Years - Continuous Service Date", "Months - Continuous Service Date", "Contract Start Date",
        "Start Date (Remotely)", "Date of Move", "Clawback End Date", "Assignment End Date", "Mobility Support Type",
        "Manager's MUD ID", "Manager's Employee ID", "Worker's Manager", "Manager's Business Title", "Manager's Supervisory Organisation",
        "Manager's Email", "Manager's Country", "Manager's Location", "Date of Birth", "Age", "Country of Birth", "City of Birth",
        "Gender", "Home Phones", "Payroll ID", "Legacy ID", "Pay Group", "Number of Direct Reports", "Levels from Top of Organisation (CEO=2)",
        "CEO", "CEO Business Title", "CET", "CET Business Title", "CET-1", "CET-1 Business Title", "CET-2", "CET-2 Business Title",
        "CET-3", "CET-3 Business Title", "CET-4", "CET-4 Business Title", "CET-5", "CET-5 Business Title", "CET-6", "CET-6 Business Title",
        "Management Levels (Benefit Jobs)", "Base Salary", "Car Allowance", "Sports Allowance", "Transportation Allowance"]

# Eksik sütun var mı diye güvenlik kontrolü yapıp dataframe'i oluşturuyoruz
existing_cols = [c for c in cols if c in df.columns]
df = df[existing_cols]

# Bilerek Yinelenen (Duplicate) Satırlar Ekleyelim (EDA/Temizlik aşaması yakalasın diye)
duplicates = df.sample(n=20, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

df.to_csv('raw_worker_details.csv', index=False)

print(f"📊 Toplam Satır Sayısı: {len(df)}")
print("\n📊 TERMİNATİON REASON DAĞILIMI (Yeni Korelasyonlu Dağılım):")
print(df['Termination Reason'].value_counts(dropna=False))
print("\n✅ Başarılı! ML uyumlu 'raw_worker_details.csv' dosyası organik ilişkilerle üretildi.")
