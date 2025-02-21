import pandas as pd
import random
import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session

app = Flask(__name__, static_folder="static")
app.secret_key = "Election@2025"

UPLOAD_FOLDER = "uploads"
OUTPUT_FILE = "randomized_teams.xlsx"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

REQUIRED_COLUMNS = ['Employee Code', 'Employee Name', 'Designation', 'Department',
                    'Office Address', 'Mobile', 'Officer Designation at the Polling Stations']

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            flash("No file selected. Please upload an Excel file.", "error")
            return redirect(url_for("upload_file"))

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
        uploaded_file.save(file_path)

        try:
            teams_list, missing_columns = process_randomization(file_path)

            if missing_columns:
                flash("Missing Required Columns:", "error")
                session["missing_columns"] = missing_columns
                return redirect(url_for("upload_file"))

            session["teams_list"] = teams_list
            return render_template("upload.html", teams=teams_list, required_columns=REQUIRED_COLUMNS)

        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("upload_file"))
        except Exception as e:
            flash("An unexpected error occurred. Please check the file format and try again.", "error")
            return redirect(url_for("upload_file"))

    teams_list = session.pop("teams_list", None)
    missing_columns = session.pop("missing_columns", None)
    return render_template("upload.html", teams=teams_list, missing_columns=missing_columns, required_columns=REQUIRED_COLUMNS)

@app.route("/download")
def download_file():
    return send_file(OUTPUT_FILE, as_attachment=True)

def process_randomization(file_path):
    df = pd.read_excel(file_path)

    missing_columns = list(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        return None, missing_columns

    opo_candidates = df[df['Officer Designation at the Polling Stations'].isin(['Other Polling Officer', 'OPO'])].sample(frac=1).reset_index(drop=True)
    po_candidates = df[df['Officer Designation at the Polling Stations'].isin(['Presiding Officer', 'PO'])].sample(frac=1).reset_index(drop=True)

    num_polling_stations = 50
    if len(po_candidates) < num_polling_stations or len(opo_candidates) < num_polling_stations * 3:
        raise ValueError("Not enough POs or OPOs for 50 teams.")

    team_data = []
    for i in range(num_polling_stations):
        team_code = f"pdp-25-{1001 + i}"
        po = po_candidates.iloc[i]
        team_data.append([team_code, po["Employee Code"], po["Employee Name"], po["Designation"], 
                          po["Department"], po["Office Address"], po["Mobile"], "Presiding Officer"])

        for j in range(3):
            opo = opo_candidates.iloc[i * 3 + j]
            team_data.append([team_code, opo["Employee Code"], opo["Employee Name"], opo["Designation"], 
                              opo["Department"], opo["Office Address"], opo["Mobile"], "Other Polling Officer"])

    columns = ["Team Code", "Employee Code", "Employee Name", "Designation", 
               "Department", "Office Address", "Mobile", "Officer Designation at the Polling Stations"]
    teams_df = pd.DataFrame(team_data, columns=columns)

    reserved_po = po_candidates.iloc[num_polling_stations:]
    reserved_opo = opo_candidates.iloc[num_polling_stations * 3:]
    reserve_employees = pd.concat([reserved_po, reserved_opo])

    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        teams_df.to_excel(writer, sheet_name="Teams", index=False)
        reserve_employees.to_excel(writer, sheet_name="Reserve", index=False)

    return teams_df.values.tolist(), None

if __name__ == "__main__":
    app.run(debug=True)
