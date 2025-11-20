"""Database service layer for managing service types and client configurations"""
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import (
    SessionLocal, ServiceType, Client, ClientServiceConfig, 
    PeriodOverride, ConfigHistory, ManualEntry, User
)

class DatabaseService:
    """Service layer for database operations"""
    
    def __init__(self):
        self.db = None
    
    def get_session(self) -> Session:
        """Get or create database session"""
        if not self.db:
            self.db = SessionLocal()
        return self.db
    
    def close_session(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    # ===== SERVICE TYPE OPERATIONS =====
    
    def get_all_service_types(self, active_only=True) -> List[ServiceType]:
        """Get all service types"""
        db = self.get_session()
        query = db.query(ServiceType)
        if active_only:
            query = query.filter(ServiceType.is_active == True)
        return query.order_by(ServiceType.is_medical.desc(), ServiceType.name).all()
    
    def get_service_type_by_name(self, name: str) -> Optional[ServiceType]:
        """Get service type by name"""
        db = self.get_session()
        return db.query(ServiceType).filter(ServiceType.name == name).first()
    
    def create_service_type(self, name: str, is_medical: bool, default_rate: float,
                           billing_method: str = 'hourly', unit_type: str = 'hour',
                           description: str = None) -> ServiceType:
        """Create a new service type"""
        db = self.get_session()
        service_type = ServiceType(
            name=name,
            is_medical=is_medical,
            default_rate=default_rate,
            billing_method=billing_method,
            unit_type=unit_type,
            description=description
        )
        db.add(service_type)
        db.commit()
        db.refresh(service_type)
        return service_type
    
    def update_service_type(self, service_id: int, **kwargs) -> ServiceType:
        """Update a service type"""
        db = self.get_session()
        service_type = db.query(ServiceType).filter(ServiceType.id == service_id).first()
        if service_type:
            for key, value in kwargs.items():
                if hasattr(service_type, key):
                    setattr(service_type, key, value)
            db.commit()
            db.refresh(service_type)
        return service_type
    
    def delete_service_type(self, service_id: int, soft_delete: bool = True):
        """Delete a service type (soft or hard delete)"""
        db = self.get_session()
        service_type = db.query(ServiceType).filter(ServiceType.id == service_id).first()
        if service_type:
            if soft_delete:
                service_type.is_active = False
                db.commit()
            else:
                db.delete(service_type)
                db.commit()
    
    # ===== CLIENT OPERATIONS =====
    
    def get_all_clients(self, active_only=True) -> List[Client]:
        """Get all clients"""
        db = self.get_session()
        query = db.query(Client)
        if active_only:
            query = query.filter(Client.is_active == True)
        return query.order_by(Client.name).all()
    
    def get_client_by_name(self, name: str) -> Optional[Client]:
        """Get client by name"""
        db = self.get_session()
        return db.query(Client).filter(Client.name == name).first()
    
    def create_client(self, name: str, notes: str = None) -> Client:
        """Create a new client"""
        db = self.get_session()
        client = Client(name=name, notes=notes)
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    
    def get_or_create_client(self, name: str) -> Client:
        """Get existing client or create new one"""
        client = self.get_client_by_name(name)
        if not client:
            client = self.create_client(name)
        return client
    
    # ===== CLIENT SERVICE CONFIG OPERATIONS =====
    
    def get_client_configs(self, client_name: str) -> List[ClientServiceConfig]:
        """Get all service configurations for a client"""
        db = self.get_session()
        client = self.get_client_by_name(client_name)
        if not client:
            return []
        return db.query(ClientServiceConfig).filter(
            and_(
                ClientServiceConfig.client_id == client.id,
                ClientServiceConfig.is_active == True
            )
        ).all()
    
    def create_client_config(self, client_name: str, service_type_name: str,
                            default_hours: float, custom_rate: float = None,
                            billing_method: str = 'hourly', unit_type: str = 'hour') -> ClientServiceConfig:
        """Create a new client service configuration"""
        db = self.get_session()
        
        # Get or create client
        client = self.get_or_create_client(client_name)
        
        # Get service type
        service_type = self.get_service_type_by_name(service_type_name)
        if not service_type:
            raise ValueError(f"Service type '{service_type_name}' not found")
        
        # Check if config already exists
        existing = db.query(ClientServiceConfig).filter(
            and_(
                ClientServiceConfig.client_id == client.id,
                ClientServiceConfig.service_type_id == service_type.id,
                ClientServiceConfig.is_active == True
            )
        ).first()
        
        if existing:
            # Update existing config
            existing.default_hours = default_hours
            existing.custom_rate = custom_rate
            existing.billing_method = billing_method
            existing.unit_type = unit_type
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new config
            config = ClientServiceConfig(
                client_id=client.id,
                service_type_id=service_type.id,
                default_hours=default_hours,
                custom_rate=custom_rate,
                billing_method=billing_method,
                unit_type=unit_type
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            return config
    
    def get_service_rate(self, service_type_name: str) -> Dict[str, Any]:
        """Get service rate information"""
        service_type = self.get_service_type_by_name(service_type_name)
        if service_type:
            return {
                'rate': service_type.default_rate,
                'billing_method': service_type.billing_method,
                'unit': service_type.unit_type,
                'is_medical': service_type.is_medical
            }
        return {
            'rate': 0.0,
            'billing_method': 'hourly',
            'unit': 'hour',
            'is_medical': False
        }
    
    def get_all_service_rates(self) -> Dict[str, Dict[str, Any]]:
        """Get all service rates as a dictionary"""
        service_types = self.get_all_service_types()
        return {
            st.name: {
                'rate': st.default_rate,
                'billing_method': st.billing_method,
                'unit': st.unit_type,
                'is_medical': st.is_medical
            }
            for st in service_types
        }
    
    def update_service_rate(self, service_type_name: str, rate: float):
        """Update service type rate"""
        db = self.get_session()
        service_type = self.get_service_type_by_name(service_type_name)
        if service_type:
            service_type.default_rate = rate
            db.commit()
    
    def get_service_type_names(self, medical_only=False, non_medical_only=False) -> List[str]:
        """Get list of service type names"""
        db = self.get_session()
        query = db.query(ServiceType).filter(ServiceType.is_active == True)
        
        if medical_only:
            query = query.filter(ServiceType.is_medical == True)
        elif non_medical_only:
            query = query.filter(ServiceType.is_medical == False)
        
        service_types = query.order_by(ServiceType.is_medical.desc(), ServiceType.name).all()
        return [st.name for st in service_types]
    
    # ===== MIGRATION HELPERS =====
    
    def migrate_from_json(self, json_file_path: str):
        """Migrate client data from JSON file to database"""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            for client_name, services in data.items():
                for service_name, config in services.items():
                    try:
                        self.create_client_config(
                            client_name=client_name,
                            service_type_name=service_name,
                            default_hours=config.get('default_hours', 0.0),
                            custom_rate=config.get('rate'),
                            billing_method=config.get('billing_method', 'hourly'),
                            unit_type=config.get('unit', 'hour')
                        )
                    except Exception as e:
                        print(f"Error migrating {client_name} - {service_name}: {e}")
        except FileNotFoundError:
            print(f"JSON file not found: {json_file_path}")
        except Exception as e:
            print(f"Error during migration: {e}")
    
    # ===== MANUAL ENTRY OPERATIONS =====
    
    def create_manual_entry(self, client_name: str, caregiver_name: str, 
                           service_date: datetime, service_type: str,
                           hours: float, notes: str = None) -> ManualEntry:
        """Create a new manual entry and ensure client exists in Client table"""
        db = self.get_session()
        
        # Ensure client exists in Client table
        client = self.get_client_by_name(client_name)
        if not client:
            client = self.create_client(client_name, notes=f"Auto-created from manual entry")
        
        # Create manual entry
        entry = ManualEntry(
            client_name=client_name,
            caregiver_name=caregiver_name,
            service_date=service_date,
            service_type=service_type,
            hours=hours,
            notes=notes
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    def get_all_manual_entries(self) -> List[ManualEntry]:
        """Get all manual entries"""
        db = self.get_session()
        return db.query(ManualEntry).order_by(ManualEntry.entry_date.desc()).all()
    
    def get_manual_entries_by_client(self, client_name: str) -> List[ManualEntry]:
        """Get manual entries for a specific client"""
        db = self.get_session()
        return db.query(ManualEntry).filter(ManualEntry.client_name == client_name).all()
    
    def delete_manual_entry(self, entry_id: int):
        """Delete a manual entry"""
        db = self.get_session()
        entry = db.query(ManualEntry).filter(ManualEntry.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
    
    def clear_all_manual_entries(self):
        """Delete all manual entries"""
        db = self.get_session()
        db.query(ManualEntry).delete()
        db.commit()
    
    # ===== USER AUTHENTICATION OPERATIONS =====
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if user.check_password(password):
                # Update last login time
                user.last_login = datetime.utcnow()
                db.commit()
                return user
            
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def create_user(self, username: str, password: str, email: str = None,
                   full_name: str = None, is_admin: bool = False) -> User:
        """Create a new user"""
        db = self.get_session()
        
        # Check if user already exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError(f"User '{username}' already exists")
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=is_admin
        )
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        db = self.get_session()
        return db.query(User).order_by(User.username).all()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        db = self.get_session()
        return db.query(User).filter(User.username == username).first()
    
    def update_user_password(self, username: str, new_password: str) -> bool:
        """Update user password"""
        db = self.get_session()
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.set_password(new_password)
            db.commit()
            return True
        return False
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user"""
        db = self.get_session()
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    
    def activate_user(self, username: str) -> bool:
        """Activate a user"""
        db = self.get_session()
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.is_active = True
            db.commit()
            return True
        return False
