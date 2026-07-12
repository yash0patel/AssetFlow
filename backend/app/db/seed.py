"""
app/db/seed.py
───────────────
Database seeding script for local development.
Populates realistic sample data for all modules.
Run: python -m app.db.seed
"""

import asyncio
import sys
from datetime import datetime, timezone, date, timedelta

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserProfile, Role, Permission, UserRole, RolePermission
from app.models.department import Department, AssetCategory, AssetCategoryAttribute
from app.models.employee import Employee
from app.models.asset import Asset, AssetLocation, AssetStatusHistory
from app.models.allocation import AssetAllocation
from app.models.booking import ResourceBooking
from app.models.maintenance import MaintenanceRequest, MaintenanceTechnician
from app.models.shared import EntityCodeSequence

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def seed() -> None:
    """Seed the database with initial development data."""
    async with AsyncSessionLocal() as session:
        print("Starting database seeding...")

        # ── Cleanup existing data ─────────────────────────────────────────────
        print("Cleaning up old database tables...")
        from app.models.transfer import AssetTransferRequest
        from app.models.audit import AuditCycle, AuditCycleAuditor, AuditCycleItem, AuditDiscrepancyReport
        from app.models.maintenance import MaintenanceStatusHistory
        from sqlalchemy import update

        await session.execute(delete(AuditDiscrepancyReport))
        await session.execute(delete(AuditCycleItem))
        await session.execute(delete(AuditCycleAuditor))
        await session.execute(delete(AuditCycle))
        await session.execute(delete(ResourceBooking))
        await session.execute(delete(MaintenanceStatusHistory))
        await session.execute(delete(MaintenanceRequest))
        await session.execute(delete(AssetTransferRequest))
        await session.execute(delete(AssetAllocation))
        await session.execute(delete(AssetStatusHistory))
        await session.execute(delete(Asset))
        await session.execute(delete(AssetLocation))

        # Break circular dependency between Department and Employee
        await session.execute(update(Department).values(head_employee_id=None))
        await session.flush()

        await session.execute(delete(Employee))
        await session.execute(delete(Department))
        await session.execute(delete(AssetCategoryAttribute))
        await session.execute(delete(AssetCategory))
        await session.execute(delete(UserProfile))
        await session.execute(delete(UserRole))
        await session.execute(delete(RolePermission))
        await session.execute(delete(User))
        await session.flush()

        # ── 1. Roles ──────────────────────────────────────────────────────────
        role_names = ["admin", "asset_manager", "department_head", "employee"]
        await session.execute(delete(Role).where(Role.name.not_in(role_names)))

        roles_db = {}
        for role_name in role_names:
            res = await session.execute(select(Role).where(Role.name == role_name))
            role = res.scalar_one_or_none()
            if not role:
                role = Role(name=role_name, description=f"{role_name.replace('_', ' ').capitalize()} role", is_active=True)
                session.add(role)
                print(f"  Created role: {role_name}")
            roles_db[role_name] = role
        await session.flush()

        # ── 2. Permissions ────────────────────────────────────────────────────
        permissions_list = [
            ("users.create", "Users"), ("users.read", "Users"), ("users.update", "Users"), ("users.delete", "Users"),
            ("assets.create", "Assets"), ("assets.read", "Assets"), ("assets.update", "Assets"), ("assets.delete", "Assets"),
            ("departments.create", "Departments"), ("departments.read", "Departments"),
            ("departments.update", "Departments"), ("departments.delete", "Departments"),
            ("allocations.create", "Allocations"), ("allocations.read", "Allocations"), ("allocations.update", "Allocations"),
            ("bookings.create", "Bookings"), ("bookings.read", "Bookings"), ("bookings.cancel", "Bookings"),
            ("maintenance.create", "Maintenance"), ("maintenance.read", "Maintenance"),
            ("maintenance.approve", "Maintenance"), ("maintenance.resolve", "Maintenance"),
        ]

        permissions_db = {}
        for perm_name, module in permissions_list:
            res = await session.execute(select(Permission).where(Permission.name == perm_name))
            perm = res.scalar_one_or_none()
            if not perm:
                perm = Permission(name=perm_name, module_name=module, is_active=True)
                session.add(perm)
            permissions_db[perm_name] = perm
        await session.flush()

        # Admin → all permissions
        for perm in permissions_db.values():
            res = await session.execute(select(RolePermission).where(
                (RolePermission.role_id == roles_db["admin"].id) & (RolePermission.permission_id == perm.id)
            ))
            if not res.scalar_one_or_none():
                session.add(RolePermission(role_id=roles_db["admin"].id, permission_id=perm.id))

        employee_perms = ["assets.read", "departments.read", "allocations.read",
                          "bookings.create", "bookings.read", "bookings.cancel",
                          "maintenance.create", "maintenance.read"]
        for perm_name in employee_perms:
            perm = permissions_db[perm_name]
            res = await session.execute(select(RolePermission).where(
                (RolePermission.role_id == roles_db["employee"].id) & (RolePermission.permission_id == perm.id)
            ))
            if not res.scalar_one_or_none():
                session.add(RolePermission(role_id=roles_db["employee"].id, permission_id=perm.id))
        await session.flush()

        # ── 3. Sequences ──────────────────────────────────────────────────────
        for prefix, start in [("AF", 0), ("EMP", 0), ("MR", 0)]:
            res = await session.execute(select(EntityCodeSequence).where(EntityCodeSequence.entity_prefix == prefix))
            if not res.scalar_one_or_none():
                session.add(EntityCodeSequence(entity_prefix=prefix, current_value=start, padding_length=4))
        await session.flush()

        # ── 4. Users & Employees ──────────────────────────────────────────────
        users_to_seed = [
            {"email": "admin@company.com", "password": "admin123", "first_name": "Adam", "last_name": "Smith", "role": "admin"},
            {"email": "manager@company.com", "password": "manager123", "first_name": "Maya", "last_name": "Patel", "role": "asset_manager"},
            {"email": "head@company.com", "password": "head123", "first_name": "Dhruv", "last_name": "Mehta", "role": "department_head"},
            {"email": "alice@company.com", "password": "alice123", "first_name": "Alice", "last_name": "Johnson", "role": "employee"},
            {"email": "bob@company.com", "password": "bob123", "first_name": "Bob", "last_name": "Kumar", "role": "employee"},
            {"email": "priya@company.com", "password": "priya123", "first_name": "Priya", "last_name": "Shah", "role": "employee"},
            {"email": "raj@company.com", "password": "raj123", "first_name": "Raj", "last_name": "Verma", "role": "employee"},
            {"email": "sara@company.com", "password": "sara123", "first_name": "Sara", "last_name": "Thomas", "role": "employee"},
        ]

        user_objs = {}
        for u_data in users_to_seed:
            res = await session.execute(select(User).where(User.email == u_data["email"]))
            user = res.scalar_one_or_none()
            if not user:
                user = User(email=u_data["email"], password_hash=hash_password(u_data["password"]),
                            status="Active", email_verified_at=datetime.now(timezone.utc))
                session.add(user)
                await session.flush()
                session.add(UserProfile(user_id=user.id, first_name=u_data["first_name"], last_name=u_data["last_name"]))
                print(f"  Created user: {u_data['email']}")
            user_objs[u_data["email"]] = (user, u_data["role"])

            res_ur = await session.execute(select(UserRole).where(
                (UserRole.user_id == user.id) & (UserRole.role_id == roles_db[u_data["role"]].id) & (UserRole.revoked_at.is_(None))
            ))
            if not res_ur.scalar_one_or_none():
                session.add(UserRole(user_id=user.id, role_id=roles_db[u_data["role"]].id, assigned_by=user.id))
        await session.flush()

        # ── 5. Departments ────────────────────────────────────────────────────
        admin_user_id = user_objs["admin@company.com"][0].id
        dept_names = ["IT", "Human Resources", "Finance", "Engineering", "Operations"]
        dept_objs = {}
        for dept_name in dept_names:
            res = await session.execute(select(Department).where(Department.name == dept_name))
            dept = res.scalar_one_or_none()
            if not dept:
                dept = Department(name=dept_name, code=dept_name[:3].upper(), status="Active", created_by=admin_user_id)
                session.add(dept)
                print(f"  Created department: {dept_name}")
            dept_objs[dept_name] = dept
        await session.flush()

        # ── 6. Asset Locations ────────────────────────────────────────────────
        locations_data = [
            ("HQ - Floor 1", "Floor"), ("HQ - Floor 2", "Floor"),
            ("Server Room A", "Room"), ("Conference Room B2", "Room"),
            ("Conference Room C1", "Room"), ("Remote Office", "Building"),
        ]
        location_objs = {}
        for loc_name, loc_type in locations_data:
            res = await session.execute(select(AssetLocation).where(AssetLocation.name == loc_name))
            loc = res.scalar_one_or_none()
            if not loc:
                loc = AssetLocation(name=loc_name, location_type=loc_type, is_active=True)
                session.add(loc)
            location_objs[loc_name] = loc
        await session.flush()

        # ── 7. Asset Categories ───────────────────────────────────────────────
        category_data = [
            ("Laptop", "Computing devices"), ("Desktop Computer", "Desktop PCs"),
            ("Projector", "Presentation equipment"), ("Conference Room", "Bookable rooms"),
            ("Network Equipment", "Routers, switches"), ("Office Furniture", "Desks, chairs"),
        ]
        cat_objs = {}
        for cat_name, desc in category_data:
            res = await session.execute(select(AssetCategory).where(AssetCategory.name == cat_name))
            cat = res.scalar_one_or_none()
            if not cat:
                cat = AssetCategory(name=cat_name, description=desc, default_useful_life_months=60, is_active=True)
                session.add(cat)
            cat_objs[cat_name] = cat
        await session.flush()

        # ── 8. Employees ──────────────────────────────────────────────────────
        admin_user = user_objs["admin@company.com"][0]
        emp_data = [
            ("admin@company.com", "IT", "System Administrator", None, date(2020, 1, 15)),
            ("manager@company.com", "IT", "Asset Manager", None, date(2021, 3, 1)),
            ("head@company.com", "Engineering", "Engineering Head", None, date(2020, 6, 1)),
            ("alice@company.com", "IT", "Software Engineer", None, date(2022, 1, 10)),
            ("bob@company.com", "Finance", "Financial Analyst", None, date(2022, 4, 5)),
            ("priya@company.com", "Engineering", "Senior Engineer", None, date(2021, 9, 20)),
            ("raj@company.com", "Human Resources", "HR Specialist", None, date(2023, 2, 14)),
            ("sara@company.com", "Operations", "Operations Coordinator", None, date(2022, 11, 3)),
        ]

        emp_objs = {}
        emp_code_counter = 1
        for email, dept_name, designation, mgr_email, joining_date in emp_data:
            user = user_objs[email][0]
            res = await session.execute(select(Employee).where(Employee.user_id == user.id))
            emp = res.scalar_one_or_none()
            if not emp:
                emp = Employee(
                    user_id=user.id,
                    employee_code=f"EMP-{str(emp_code_counter).zfill(4)}",
                    department_id=dept_objs[dept_name].id,
                    designation=designation,
                    date_of_joining=joining_date,
                    status="Active",
                )
                session.add(emp)
                print(f"  Created employee: {email}")
            emp_objs[email] = emp
            emp_code_counter += 1
        await session.flush()

        # Update EMP sequence
        res = await session.execute(select(EntityCodeSequence).where(EntityCodeSequence.entity_prefix == "EMP"))
        seq = res.scalar_one_or_none()
        if seq:
            seq.current_value = max(seq.current_value, emp_code_counter - 1)

        # ── 9. Technicians ────────────────────────────────────────────────────
        tech_data = [
            ("Ram Technicals", "Hardware", False, None, "9876543210"),
            ("IT Support Desk", "Software", False, None, "9123456789"),
            ("QuickFix Services", "General", True, "QuickFix Ltd.", "9000000001"),
        ]
        for t_name, spec, is_ext, vendor, contact in tech_data:
            res = await session.execute(select(MaintenanceTechnician).where(MaintenanceTechnician.name == t_name))
            if not res.scalar_one_or_none():
                session.add(MaintenanceTechnician(
                    name=t_name, specialization=spec, is_external_vendor=is_ext,
                    vendor_name=vendor, contact_number=contact, is_active=True,
                ))
        await session.flush()

        # ── 10. Assets ────────────────────────────────────────────────────────
        assets_data = [
            # (name, category, serial, status, location, department, is_bookable, cost, condition)
            ("MacBook Pro 14\"", "Laptop", "SN-MBP-001", "Allocated", "HQ - Floor 1", "IT", False, 120000, "Good"),
            ("Dell XPS 15\"", "Laptop", "SN-DXP-002", "Available", "HQ - Floor 2", "IT", False, 95000, "Good"),
            ("HP EliteBook", "Laptop", "SN-HPE-003", "Available", "HQ - Floor 1", "Engineering", False, 75000, "Good"),
            ("ThinkPad X1 Carbon", "Laptop", "SN-TPX-004", "Under Maintenance", "HQ - Floor 1", "Finance", False, 85000, "Fair"),
            ("ASUS VivoBook", "Laptop", "SN-ASV-005", "Allocated", "Remote Office", "Operations", False, 55000, "Good"),
            ("Dell OptiPlex 7090", "Desktop Computer", "SN-DOP-006", "Available", "HQ - Floor 2", "Engineering", False, 45000, "Good"),
            ("iMac 24\"", "Desktop Computer", "SN-IMC-007", "Available", "HQ - Floor 1", "IT", False, 130000, "New"),
            ("Epson EB-X51 Projector", "Projector", "SN-EPX-008", "Available", "Conference Room B2", "IT", True, 35000, "Good"),
            ("Sony VPL-EX295 Projector", "Projector", "SN-SPX-009", "Available", "Conference Room C1", "IT", True, 42000, "Good"),
            ("Conference Room B2", "Conference Room", "ROOM-B2-001", "Available", "Conference Room B2", "Operations", True, 0, "Good"),
            ("Conference Room C1", "Conference Room", "ROOM-C1-002", "Available", "Conference Room C1", "Operations", True, 0, "Good"),
            ("Cisco Switch 48-Port", "Network Equipment", "SN-CSW-012", "Available", "Server Room A", "IT", False, 65000, "New"),
            ("Ergonomic Chair", "Office Furniture", "SN-ECH-013", "Available", "HQ - Floor 1", "Operations", False, 8000, "Good"),
            ("Standing Desk", "Office Furniture", "SN-STD-014", "Allocated", "HQ - Floor 2", "Engineering", False, 15000, "Good"),
            ("HP LaserJet Printer", "Desktop Computer", "SN-HPL-015", "Retired", "HQ - Floor 1", "Human Resources", False, 25000, "Poor"),
        ]

        asset_objs = {}
        af_counter = 1
        for name, cat_name, serial, status, loc_name, dept_name, is_bookable, cost, condition in assets_data:
            res = await session.execute(select(Asset).where(Asset.serial_number == serial))
            asset = res.scalar_one_or_none()
            if not asset:
                asset = Asset(
                    asset_tag=f"AF-{str(af_counter).zfill(4)}",
                    name=name,
                    category_id=cat_objs[cat_name].id,
                    serial_number=serial,
                    current_status=status,
                    condition=condition,
                    current_location_id=location_objs[loc_name].id,
                    owning_department_id=dept_objs[dept_name].id,
                    is_bookable=is_bookable,
                    acquisition_date=date(2022, 1, 1),
                    acquisition_cost=cost,
                    created_by=admin_user.id,
                )
                session.add(asset)
            asset_objs[serial] = asset
            af_counter += 1
        await session.flush()

        # Update AF sequence
        res = await session.execute(select(EntityCodeSequence).where(EntityCodeSequence.entity_prefix == "AF"))
        seq = res.scalar_one_or_none()
        if seq:
            seq.current_value = max(seq.current_value, af_counter - 1)

        # ── 11. Allocations ───────────────────────────────────────────────────
        today = date.today()
        alloc_data = [
            ("SN-MBP-001", "alice@company.com", today - timedelta(days=30), today + timedelta(days=60)),
            ("SN-ASV-005", "raj@company.com", today - timedelta(days=45), today - timedelta(days=5)),  # overdue
            ("SN-STD-014", "priya@company.com", today - timedelta(days=20), today + timedelta(days=40)),
        ]
        alice_emp = emp_objs["alice@company.com"]
        manager_emp = emp_objs["manager@company.com"]

        for serial, emp_email, alloc_date, return_date in alloc_data:
            asset = asset_objs.get(serial)
            emp = emp_objs.get(emp_email)
            if asset and emp:
                res = await session.execute(select(AssetAllocation).where(
                    AssetAllocation.asset_id == asset.id, AssetAllocation.status == "Active"
                ))
                if not res.scalar_one_or_none():
                    session.add(AssetAllocation(
                        asset_id=asset.id,
                        allocated_to_employee_id=emp.id,
                        allocated_by=manager_emp.id,
                        allocation_date=datetime.combine(alloc_date, datetime.min.time()).replace(tzinfo=timezone.utc),
                        expected_return_date=return_date,
                        status="Active",
                    ))
                    asset.current_holder_employee_id = emp.id
        await session.flush()

        # ── 12. Maintenance Request ───────────────────────────────────────────
        mr_asset = asset_objs.get("SN-HPE-003")
        if mr_asset:
            res = await session.execute(select(MaintenanceRequest).where(MaintenanceRequest.asset_id == mr_asset.id))
            if not res.scalar_one_or_none():
                session.add(MaintenanceRequest(
                    request_code="MR-0001",
                    asset_id=mr_asset.id,
                    raised_by_employee_id=alice_emp.id,
                    issue_description="Screen flickering intermittently. Possible hardware fault.",
                    priority="High",
                    status="Pending",
                ))
        await session.flush()

        # ── 13. Bookings ──────────────────────────────────────────────────────
        room_asset = asset_objs.get("ROOM-B2-001")
        alice_emp_obj = emp_objs.get("alice@company.com")
        if room_asset and alice_emp_obj:
            tomorrow = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            res = await session.execute(select(ResourceBooking).where(
                ResourceBooking.asset_id == room_asset.id,
                ResourceBooking.status == "Upcoming",
            ))
            if not res.scalar_one_or_none():
                session.add(ResourceBooking(
                    asset_id=room_asset.id,
                    booked_by_employee_id=alice_emp_obj.id,
                    department_id=dept_objs["IT"].id,
                    start_datetime=tomorrow,
                    end_datetime=tomorrow + timedelta(hours=1),
                    purpose="Sprint Planning Meeting",
                    status="Upcoming",
                ))
        await session.flush()

        # Update MR sequence
        res = await session.execute(select(EntityCodeSequence).where(EntityCodeSequence.entity_prefix == "MR"))
        seq = res.scalar_one_or_none()
        if seq:
            seq.current_value = max(seq.current_value, 1)

        await session.commit()
        print("Database seeding complete!")
        print("  Credentials: admin@company.com / admin123")
        print("  Credentials: manager@company.com / manager123")
        print("  Credentials: alice@company.com / alice123")


if __name__ == "__main__":
    asyncio.run(seed())
