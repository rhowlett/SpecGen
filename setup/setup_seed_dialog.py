"""
setup_seed_dialog.py — First-run company & user seeding dialog.

Opened by the setup GUI when kicad_specgen_local.json does not yet exist.
Flow (per the source documents):

  1. Seed defaults from KSG_APP_DIR; user chooses KSG_COMPANY_DIR.
  2. If KSG_COMPANY_DIR/SpecGen/kicad_specgen_company.json exists, load it.
       - If users exist, let the user select one → derive KSG_USER_*_DIR
         using the documented convention.
       - If no users exist, prompt to create one → create user folders.
  3. Else, create the SpecGen folder structure, seed the JSON files, then
     prompt to populate company + user info and save.

Returns, via .result_tokens, a dict of the resolved writable tokens plus the
selected worker_id, so setup can write kicad_specgen_local.json.
"""
from __future__ import annotations
import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QDialogButtonBox, QMessageBox,
    QFileDialog, QGroupBox,
)

log = logging.getLogger("setup.seed")


class FirstRunSeedDialog(QDialog):
    def __init__(self, app_dir: Path, parent=None) -> None:
        super().__init__(parent)
        self._app_dir = Path(app_dir)
        self.result_tokens: dict | None = None
        self.setWindowTitle("KiCad SpecGen — First-Run Setup")
        self.setMinimumWidth(640)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<h3>Company & User Setup</h3>"
            "Choose your shared company folder. SpecGen will read or create "
            "the company configuration there and set up your user folders."
        ))

        # Company dir chooser (seeded to KSG_APP_DIR)
        box = QGroupBox("Company Folder (KSG_COMPANY_DIR)")
        bl = QFormLayout(box)
        row = QHBoxLayout()
        self._company_dir_edit = QLineEdit(str(self._app_dir))
        btn_choose = QPushButton("Choose Folder")
        btn_choose.clicked.connect(self._choose_company_dir)
        row.addWidget(self._company_dir_edit)
        row.addWidget(btn_choose)
        bl.addRow("Folder:", row)
        btn_scan = QPushButton("Scan for company configuration")
        btn_scan.clicked.connect(self._scan_company)
        bl.addRow(btn_scan)
        layout.addWidget(box)

        # User selection / creation
        self._user_box = QGroupBox("User")
        ul = QFormLayout(self._user_box)
        self._user_combo = QComboBox()
        self._user_combo.addItem("(create new user)", "")
        ul.addRow("Select User:", self._user_combo)
        self._new_worker_id = QLineEdit()
        self._new_display   = QLineEdit()
        self._new_family    = QLineEdit()
        ul.addRow("New Worker ID:",    self._new_worker_id)
        ul.addRow("New Display Name:", self._new_display)
        ul.addRow("New Family Name:",  self._new_family)
        layout.addWidget(self._user_box)

        self._status = QLabel("Choose a company folder and scan to begin.")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        buttons = QDialogButtonBox()
        self._btn_ok = buttons.addButton("Create / Continue",
                                         QDialogButtonBox.ButtonRole.AcceptRole)
        cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        self._btn_ok.clicked.connect(self._on_continue)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

        self._company_cfg = None

    def _choose_company_dir(self) -> None:
        seed = self._company_dir_edit.text() or str(self._app_dir)
        folder = QFileDialog.getExistingDirectory(self, "Choose Folder", seed)
        if folder:
            self._company_dir_edit.setText(folder)

    def _company_json_path(self) -> Path:
        return (Path(self._company_dir_edit.text())
                / "SpecGen" / "kicad_specgen_company.json")

    def _users_json_path(self) -> Path:
        return (Path(self._company_dir_edit.text())
                / "SpecGen" / "kicad_specgen_users.json")

    def _scan_company(self) -> None:
        import core.specgen_company_config as company_mod
        import core.specgen_user_config as users_mod
        company_path = self._company_json_path()
        self._user_combo.clear()
        self._user_combo.addItem("(create new user)", "")

        if company_path.exists():
            self._company_cfg = company_mod.load(company_path)
            users_path = self._users_json_path()
            n_users = 0
            if users_path.exists():
                ucfg = users_mod.load(users_path)
                for u in ucfg.users:
                    self._user_combo.addItem(
                        f"{u.get('display_name','')} [{u.get('worker_id','')}]",
                        u.get("worker_id", ""))
                    n_users += 1
            self._status.setText(
                f"Found company configuration ({self._company_cfg.company_name}). "
                f"{n_users} user(s). Select an existing user or create a new one."
            )
        else:
            self._company_cfg = None
            self._status.setText(
                "No company configuration found here. Continuing will create "
                "the SpecGen folder structure and a new company + user."
            )

    def _on_continue(self) -> None:
        import core.specgen_company_config as company_mod
        import core.specgen_user_config as users_mod

        company_dir = self._company_dir_edit.text().strip()
        if not company_dir:
            QMessageBox.warning(self, "Folder Required",
                                "Choose a company folder first."); return

        specgen_dir = Path(company_dir) / "SpecGen"
        company_path = self._company_json_path()
        users_path   = self._users_json_path()
        specgen_dir.mkdir(parents=True, exist_ok=True)

        # Create company/users files if missing
        if not company_path.exists():
            company_mod.create_standalone(company_path)
        if not users_path.exists():
            users_mod.create_empty(users_path)
        ucfg = users_mod.load(users_path)

        # Determine the worker_id
        selected = self._user_combo.currentData()
        if selected:
            worker_id = selected
        else:
            worker_id = self._new_worker_id.text().strip()
            if not worker_id:
                QMessageBox.warning(self, "Worker ID Required",
                                    "Enter a Worker ID for the new user."); return
            if worker_id in ucfg.worker_ids:
                QMessageBox.warning(self, "Duplicate",
                                    f"Worker ID '{worker_id}' already exists."); return
            ucfg.users.append({
                "worker_id": worker_id,
                "display_name": self._new_display.text().strip() or worker_id,
                "family_name": self._new_family.text().strip(),
                "worker_type": "employee",
                "active": True,
                "is_admin": True,
                "client_assignments": [],
            })
            users_mod.save(ucfg)
            users_mod.create_user_folders(company_dir, worker_id)

        # Derive user dirs per the documented convention
        user_specgen, user_common = users_mod.derive_user_dirs(company_dir, worker_id)

        # Seed company writable dirs (shared, under SpecGen/)
        company_specgen = str(specgen_dir / "specgen")
        company_common  = str(specgen_dir / "common")
        Path(company_specgen).mkdir(parents=True, exist_ok=True)
        Path(company_common).mkdir(parents=True, exist_ok=True)

        self.result_tokens = {
            "KSG_COMPANY_DIR":         company_dir,
            "KSG_COMPANY_SPECGEN_DIR": company_specgen,
            "KSG_COMPANY_COMMON_DIR":  company_common,
            "KSG_USER_SPECGEN_DIR":    user_specgen,
            "KSG_USER_COMMON_DIR":     user_common,
            "active_user":             worker_id,
        }
        self.accept()
