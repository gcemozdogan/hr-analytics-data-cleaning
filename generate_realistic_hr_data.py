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
locations = ['Istanbul', 'Sütlüce', 'Gebze', 'Çayırova', 'Bolu']  # Eksiksiz tanımlandı
genders = ['Male', 'Female', 'M', 'F', 'm', 'f', 'MALE', 'FEMALE', 'Erkek', 'Kadın']
worker_types = ['Employee', 'Contingent Worker', 'Contractor']

# Termination Kategorileri (Modelin doğru eğitilmesi için en az 400 kayıt kuralı)
termination_reasons = [
    'Lack of Promotion', 'Pay Dissatisfaction', 'Career Development',
    'Personal Reasons', 'Relocation', 'Work-Life Balance / Burnout',
    'Health Reasons', 'Retirement'
]

# Toplam satırın %40'ını (1600 kişi) geçmiş/güncel işten ayrılmış (Terminated) yapıyoruz
n_terminated = int(NUM_ROWS * 0.40)
terminated_indices = set(random.sample(range(NUM_ROWS), n_terminated))
active_indices = list(set(range(NUM_ROWS)) - terminated_indices)

# Tam olarak %20'yi "On Leave" yapıyoruz
on_leave_indices = set(random.sample(active_indices, int(NUM_ROWS * 0.20)))

on_leave_list = list(on_leave_indices)
maternity_indices = set(on_leave_list[:int(len(on_leave_list)*0.03)])
military_indices = set(on_leave_list[int(len(on_leave_list)*0.03):int(len(on_leave_list)*0.05)])
sick_indices = set(on_leave_list[int(len(on_leave_list)*0.05):int(len(on_leave_list)*0.15)])
annual_indices = set(on_leave_list[int(len(on_leave_list)*0.15):])

# Minimum 400 kayıt kuralını garanti etmek için sayaçlar
term_counts = {reason: 0 for reason in termination_reasons}
min_required = 400

data = []

for i in range(NUM_ROWS):
    emp_id = 10000 + i

    # Ham veride EDA (Keşif) ve Temizlik testi için isimleri ve ünvanları bilerek küçük harf yapıyoruz
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}".lower()

    hire_date = fake.date_between(start_date='-10y', end_date='today')
    dob = fake.date_of_birth(minimum_age=18, maximum_age=65)

    pos_info = random.choices(positions, weights=dept_weights, k=1)[0]
    department = pos_info['Departman']

    # Typo testi için Human Resources departmanına bilinçli olarak Adminastrative hatası enjekte ediyoruz
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

    # Grade midpoint hesaplaması ve Compa-Ratio (Modelleme için kritik)
    grade_midpoint = (min_salary + max_salary) / 2
    compa_ratio = round(base_salary / grade_midpoint, 2)

    car_allowance = fake.random_int(min=2000, max=10000) if grade <= 5 else 0
    sports_allowance = fake.random_int(min=500, max=1500)
    transport_allowance = fake.random_int(min=1000, max=3000)

    last_promo_years = round(random.uniform(0.5, 6.0), 1)
    years_in_pos = round(random.uniform(0.1, 5.0), 1)
    age = (datetime.now().date() - dob).days // 365

    # STATUS ve TERMINATION REASON Kurgusu (Nedensellik bağı ile)
    if i in terminated_indices:
        status = 'Terminated'
        end_date = fake.date_between(start_date=hire_date, end_date='today')

        # 400 kayıt kuralını ve nedenselliği sağlayan mantık
        forced_reason = None
        if term_counts['Lack of Promotion'] < min_required and last_promo_years > 3.0:
            forced_reason = 'Lack of Promotion'
        elif term_counts['Pay Dissatisfaction'] < min_required and compa_ratio < 0.88:
            forced_reason = 'Pay Dissatisfaction'
        elif term_counts['Career Development'] < min_required and years_in_pos > 2.5:
            forced_reason = 'Career Development'

        if forced_reason:
            termination_reason = forced_reason
        else:
            if compa_ratio < 0.88 and random.random() < 0.35:
                termination_reason = 'Pay Dissatisfaction'
            elif last_promo_years > 3.0 and random.random() < 0.35:
                termination_reason = 'Lack of Promotion'
            elif years_in_pos > 3.0 and random.random() < 0.30:
                termination_reason = 'Career Development'
            elif age > 56 and random.random() < 0.60:
                termination_reason = 'Retirement'
            else:
                other_reasons = ['Personal Reasons', 'Relocation', 'Work-Life Balance / Burnout', 'Health Reasons']
                termination_reason = random.choices(other_reasons, weights=[0.35, 0.20, 0.30, 0.15], k=1)[0]

        if termination_reason in term_counts:
            term_counts[termination_reason] += 1
    else:
        status = 'Active'
        end_date = np.nan
        termination_reason = np.nan

    # LEAVE (İzin) ve CİNSİYET Kurgusu
    gender = random.choice(genders)

    if i in on_leave_indices:
        leave_status = "On Leave"
        if i in maternity_indices:
            leave_type = "Maternity Leave"
            gender = random.choice(['Female', 'F', 'f', 'FEMALE', 'Kadın'])
        elif i in military_indices:
            leave_type = "Military Leave"
            gender = random.choice(['Male', 'M', 'm', 'MALE', 'Erkek'])
        elif i in sick_indices:
            leave_type = "Sick Leave"
        else:
            leave_type = "Annual Leave"
    else:
        leave_status = "Not on Leave"
        leave_type = np.nan

    row = {
        "Employee ID": emp_id,
        "Full Legal Name": full_name,
        "Status": status,
        "Leave Status": leave_status,
        "Leave Type": leave_type,
        "Termination Reason": termination_reason,
        "Compa-Ratio": compa_ratio,
        "Last Promotion Years Ago": last_promo_years,
        "MUD ID": f"MUD{emp_id}",
        "Email - Work": f"{first_name.lower()}.{last_name.lower()}@beko.com",
        "Position ID": f"POS-{fake.random_int(min=100, max=999)}",
        "Position": job_title,
        "Effective Date for Current Position": hire_date + timedelta(days=random.randint(0, 365)),
        "Years in Current Position": years_in_pos,
        "Business Title": job_title,
        "Job Title": job_title,
        "Worker Type": random.choice(worker_types),
        "Employee\\ CW Type": "Regular",
        "Is International Assignee": random.choice(['Yes', 'No']),
        "Is Manager": 'Yes' if pos_info['Kariyer Track'] == 'Manager' else 'No',
        "Scheduled Weekly Hours": random.choice([40, 45, np.nan, 80]),
        "Default Weekly Hours": 45,
        "FTE %": random.choice([100, 50, 0]),
        "Work Shift": "Day",
        "Country": random.choice(countries),
        "Company Code": "BEKO01",
        "Company": "Beko",
        "Location": random.choice(locations),
        "Business Unit": department_name,
        "Sub-function": "Operations",
        "Supervisory Organization": f"{department} Org",
        "Supervisory Org ID": f"ORG-{fake.random_int(min=100, max=199)}",
        "Region": "EMEA",
        "Cost Center - ID": fake.random_int(min=1000, max=9999),
        "Cost Center - Name": f"CC-{department}",
        "Cost Center Hierarchy": "Global -> EMEA",
        "Job Category": "Professional",
        "Job Family Group": "Corporate",
        "Job Family": department,
        "Job Profile": job_title,
        "Job Code": f"JC-{grade}-{fake.random_int(min=10, max=99)}",
        "End Employment Date": end_date,
        "Company Service Date": hire_date,
        "Original Hire Date": hire_date,
        "Hire Date": hire_date,
        "Is Rehire": "No",
        "Continuous Service Date": hire_date,
        "Years - Continuous Service Date": round(random.uniform(0.1, 10), 1),
        "Months - Continuous Service Date": random.randint(1, 120),
        "Contract Start Date": hire_date,
        "Start Date (Remotely)": np.nan,
        "Date of Move": np.nan,
        "Clawback End Date": np.nan,
        "Assignment End Date": np.nan,
        "Mobility Support Type": np.nan,
        "Manager's MUD ID": "MUD9999",
        "Manager's Employee ID": "9999",
        "Worker's Manager": manager_title,
        "Manager's Business Title": manager_title,
        "Manager's Supervisory Organisation": f"{department} Org",
        "Manager's Email": "manager@beko.com",
        "Manager's Country": "Turkey",
        "Manager's Location": "Istanbul",
        "Date of Birth": dob,
        "Age": age,
        "Country of Birth": random.choice(countries),
        "City of Birth": fake.city(),
        "Gender": gender,
        "Home Phones": fake.phone_number(),
        "Payroll ID": f"PAY-{emp_id}",
        "Legacy ID": np.nan,
        "Pay Group": "Monthly",
        "Number of Direct Reports": random.randint(0, 10) if pos_info['Kariyer Track'] == 'Manager' else 0,
        "Levels from Top of Organisation (CEO=2)": grade,
        "CEO": "Hakan Bulgurlu",
        "CEO Business Title": "CEO",
        "CET": np.nan, "CET Business Title": np.nan, "CET-1": np.nan, "CET-1 Business Title": np.nan,
        "CET-2": np.nan, "CET-2 Business Title": np.nan, "CET-3": np.nan, "CET-3 Business Title": np.nan,
        "CET-4": np.nan, "CET-4 Business Title": np.nan, "CET-5": np.nan, "CET-5 Business Title": np.nan,
        "CET-6": np.nan, "CET-6 Business Title": np.nan, "Management Levels (Benefit Jobs)": np.nan,

        "Base Salary": base_salary,
        "Car Allowance": car_allowance,
        "Sports Allowance": sports_allowance,
        "Transportation Allowance": transport_allowance
    }
    data.append(row)

df = pd.DataFrame(data)

# Bilerek Yinelenen (Duplicate) Satırlar Ekleyelim (Temizlik aşaması yakalasın diye)
duplicates = df.sample(n=20, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

df.to_csv('raw_worker_details.csv', index=False)

print(f"📊 Toplam Satır Sayısı: {len(df)}")
print("📊 TERMİNATİON REASON DAĞILIMI:")
print(df['Termination Reason'].value_counts(dropna=False))
print("\n✅ Başarılı! 'raw_worker_details.csv' dosyası eksiksiz olarak oluşturuldu.")
