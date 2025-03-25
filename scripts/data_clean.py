import pandas as pd

patients_data = pd.read_csv('data/synthea_dataset/patients.csv')
appointments_data = pd.read_csv('data/synthea_dataset/appointments.csv')
doctors_data = pd.read_csv('data/synthea_dataset/doctors.csv')
cms_data = pd.read_csv('data/cms_dataset/hospital_readmissions_reduction_program_hospital.csv')

patients_data = patients_data.rename(columns={'Id': 'patient_id'})
appointments_data = appointments_data.rename(columns={'PATIENT': 'patient_id', 'PROVIDER': 'provider_id'})
doctors_data = doctors_data.rename(columns={'Id': 'provider_id'})[['provider_id', 'NAME']]

def combine_names(row):
    first = str(row['FIRST']).strip() if pd.notna(row['FIRST']) else ''
    middle = str(row['MIDDLE']).strip() if pd.notna(row['MIDDLE']) else ''
    last = str(row['LAST']).strip() if pd.notna(row['LAST']) else ''

    name_parts = [first]
    if middle:
        name_parts.append(middle)
    name_parts.append(last)
    
    return ' '.join(name_parts).strip()

patients_data['patient_name'] = patients_data.apply(combine_names, axis=1)

# cols = patients_data.columns.tolist()
# cols.remove('patient_name') 
# cols.insert(1, 'patient_name')
# patients_data = patients_data[cols]


appointments_data = pd.merge(
    appointments_data,
    doctors_data,
    on='provider_id',
    how='left'
)

appointments_data.fillna({'NAME': 'Unknown Provider'}, inplace=True)

cms_data['Number of Readmissions'] = cms_data['Number of Readmissions'].replace("Too Few to Report", 0)

patients_data.fillna(0, inplace=True)
appointments_data.fillna(0, inplace=True)
cms_data.fillna(0, inplace=True)

patients_data.to_csv('data/processed/patients_data_cleaned.csv', index=False)
appointments_data.to_csv('data/processed/appointments_data_cleaned.csv', index=False)
cms_data.to_csv('data/processed/cms_data_cleaned.csv', index=False)

