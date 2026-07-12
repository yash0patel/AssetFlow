"""
app/db/seed.py
───────────────
Database seeding script for local development.
Populates base roles, default permissions, and mock admin/employee accounts.
Run: python -m app.db.seed
"""

import asyncio
import sys
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserProfile, Role, Permission, UserRole, RolePermission

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def seed() -> None:
    """Seed the database with initial development data."""
    async with AsyncSessionLocal() as session:
        print("Starting database seeding...")
        
        # Delete roles not in simplified list and clean junctions
        from sqlalchemy import delete
        await session.execute(delete(UserRole))
        await session.execute(delete(RolePermission))
        
        # 1. Base Roles
        role_names = ["admin", "asset_manager", "department_head", "employee"]
        await session.execute(delete(Role).where(Role.name.not_in(role_names)))
        roles_db = {}
        for role_name in role_names:
            stmt = select(Role).where(Role.name == role_name)
            res = await session.execute(stmt)
            role = res.scalar_one_or_none()
            if not role:
                role = Role(
                    name=role_name,
                    description=f"{role_name.replace('_', ' ').capitalize()} role",
                    is_active=True
                )
                session.add(role)
                print(f"Created role: {role_name}")
            roles_db[role_name] = role
        
        # Flush to get role IDs
        await session.flush()
        
        # 2. Permissions
        permissions_list = [
            ("users.create", "Users"),
            ("users.read", "Users"),
            ("users.update", "Users"),
            ("users.delete", "Users"),
            ("assets.create", "Assets"),
            ("assets.read", "Assets"),
            ("assets.update", "Assets"),
            ("assets.delete", "Assets"),
            ("departments.create", "Departments"),
            ("departments.read", "Departments"),
            ("departments.update", "Departments"),
            ("departments.delete", "Departments"),
            ("allocations.create", "Allocations"),
            ("allocations.read", "Allocations"),
            ("allocations.update", "Allocations"),
            ("bookings.create", "Bookings"),
            ("bookings.read", "Bookings"),
            ("bookings.cancel", "Bookings"),
        ]
        
        permissions_db = {}
        for perm_name, module in permissions_list:
            stmt = select(Permission).where(Permission.name == perm_name)
            res = await session.execute(stmt)
            perm = res.scalar_one_or_none()
            if not perm:
                perm = Permission(
                    name=perm_name,
                    module_name=module,
                    is_active=True
                )
                session.add(perm)
                print(f"Created permission: {perm_name}")
            permissions_db[perm_name] = perm
            
        await session.flush()
        
        # 3. Associate permissions to roles
        # Admin gets all permissions
        for perm in permissions_db.values():
            stmt = select(RolePermission).where(
                (RolePermission.role_id == roles_db["admin"].id) &
                (RolePermission.permission_id == perm.id)
            )
            res = await session.execute(stmt)
            assoc = res.scalar_one_or_none()
            if not assoc:
                assoc = RolePermission(
                    role_id=roles_db["admin"].id,
                    permission_id=perm.id
                )
                session.add(assoc)
        
        # Employee gets read permission and booking permissions
        employee_perms = [
            "assets.read",
            "departments.read",
            "allocations.read",
            "bookings.create",
            "bookings.read",
            "bookings.cancel",
        ]
        for perm_name in employee_perms:
            perm = permissions_db[perm_name]
            stmt = select(RolePermission).where(
                (RolePermission.role_id == roles_db["employee"].id) &
                (RolePermission.permission_id == perm.id)
            )
            res = await session.execute(stmt)
            assoc = res.scalar_one_or_none()
            if not assoc:
                assoc = RolePermission(
                    role_id=roles_db["employee"].id,
                    permission_id=perm.id
                )
                session.add(assoc)

        await session.flush()

        # 4. Default Seed Users
        users_to_seed = [
            {
                "email": "admin@company.com",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin"
            },
            {
                "email": "employee@company.com",
                "password": "emp123",
                "first_name": "Jane",
                "last_name": "Doe",
                "role": "employee"
            }
        ]

        for u_data in users_to_seed:
            stmt = select(User).where(User.email == u_data["email"])
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()
            
            if not user:
                # Create user
                user = User(
                    email=u_data["email"],
                    password_hash=hash_password(u_data["password"]),
                    status="Active",
                    email_verified_at=datetime.now(timezone.utc)
                )
                session.add(user)
                await session.flush()
                
                # Create profile
                profile = UserProfile(
                    user_id=user.id,
                    first_name=u_data["first_name"],
                    last_name=u_data["last_name"]
                )
                session.add(profile)
                
            # Ensure the user has the seeded role assigned
            stmt_check_ur = select(UserRole).where(
                (UserRole.user_id == user.id) &
                (UserRole.role_id == roles_db[u_data["role"]].id) &
                (UserRole.revoked_at.is_(None))
            )
            res_ur = await session.execute(stmt_check_ur)
            existing_ur = res_ur.scalar_one_or_none()
            if not existing_ur:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=roles_db[u_data["role"]].id,
                    assigned_by=user.id # Self-assigned for initial seeding
                )
                session.add(user_role)
                print(f"Seeded user: {u_data['email']} with role {u_data['role']}")
        
        await session.commit()
        print("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
