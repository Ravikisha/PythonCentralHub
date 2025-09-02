# JSON Data Validator

import json
import os
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

class ValidationError:
    def __init__(self, path: str, message: str, expected: str = None, actual: str = None):
        self.path = path
        self.message = message
        self.expected = expected
        self.actual = actual
    
    def __str__(self):
        result = f"Path: {self.path} - {self.message}"
        if self.expected:
            result += f" (Expected: {self.expected}"
            if self.actual:
                result += f", Got: {self.actual}"
            result += ")"
        return result

class JSONSchema:
    def __init__(self, schema: Dict):
        self.schema = schema
        self.errors = []
    
    def validate(self, data: Any, path: str = "root") -> Tuple[bool, List[ValidationError]]:
        """Validate data against schema"""
        self.errors = []
        self._validate_recursive(data, self.schema, path)
        return len(self.errors) == 0, self.errors
    
    def _validate_recursive(self, data: Any, schema: Dict, path: str):
        """Recursively validate data against schema"""
        # Check type
        if "type" in schema:
            if not self._validate_type(data, schema["type"], path):
                return
        
        # Check required fields for objects
        if isinstance(data, dict) and "required" in schema:
            self._validate_required_fields(data, schema["required"], path)
        
        # Check properties for objects
        if isinstance(data, dict) and "properties" in schema:
            self._validate_properties(data, schema["properties"], path)
        
        # Check array items
        if isinstance(data, list) and "items" in schema:
            self._validate_array_items(data, schema["items"], path)
        
        # Check constraints
        self._validate_constraints(data, schema, path)
    
    def _validate_type(self, data: Any, expected_type: str, path: str) -> bool:
        """Validate data type"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        if expected_type not in type_mapping:
            self.errors.append(ValidationError(path, f"Unknown type: {expected_type}"))
            return False
        
        expected_python_type = type_mapping[expected_type]
        
        if not isinstance(data, expected_python_type):
            actual_type = type(data).__name__
            self.errors.append(ValidationError(
                path, "Type mismatch", expected_type, actual_type
            ))
            return False
        
        return True
    
    def _validate_required_fields(self, data: Dict, required_fields: List[str], path: str):
        """Validate required fields in object"""
        for field in required_fields:
            if field not in data:
                self.errors.append(ValidationError(
                    f"{path}.{field}", f"Required field '{field}' is missing"
                ))
    
    def _validate_properties(self, data: Dict, properties: Dict, path: str):
        """Validate object properties"""
        for key, value in data.items():
            if key in properties:
                self._validate_recursive(value, properties[key], f"{path}.{key}")
            # Note: Additional properties are allowed by default
    
    def _validate_array_items(self, data: List, items_schema: Dict, path: str):
        """Validate array items"""
        for i, item in enumerate(data):
            self._validate_recursive(item, items_schema, f"{path}[{i}]")
    
    def _validate_constraints(self, data: Any, schema: Dict, path: str):
        """Validate additional constraints"""
        # String constraints
        if isinstance(data, str):
            if "minLength" in schema and len(data) < schema["minLength"]:
                self.errors.append(ValidationError(
                    path, f"String too short (min: {schema['minLength']})", 
                    str(schema["minLength"]), str(len(data))
                ))
            
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                self.errors.append(ValidationError(
                    path, f"String too long (max: {schema['maxLength']})",
                    str(schema["maxLength"]), str(len(data))
                ))
            
            if "pattern" in schema:
                if not re.match(schema["pattern"], data):
                    self.errors.append(ValidationError(
                        path, f"String does not match pattern: {schema['pattern']}"
                    ))
        
        # Number constraints
        if isinstance(data, (int, float)):
            if "minimum" in schema and data < schema["minimum"]:
                self.errors.append(ValidationError(
                    path, f"Number too small (min: {schema['minimum']})",
                    str(schema["minimum"]), str(data)
                ))
            
            if "maximum" in schema and data > schema["maximum"]:
                self.errors.append(ValidationError(
                    path, f"Number too large (max: {schema['maximum']})",
                    str(schema["maximum"]), str(data)
                ))
        
        # Array constraints
        if isinstance(data, list):
            if "minItems" in schema and len(data) < schema["minItems"]:
                self.errors.append(ValidationError(
                    path, f"Array too short (min items: {schema['minItems']})",
                    str(schema["minItems"]), str(len(data))
                ))
            
            if "maxItems" in schema and len(data) > schema["maxItems"]:
                self.errors.append(ValidationError(
                    path, f"Array too long (max items: {schema['maxItems']})",
                    str(schema["maxItems"]), str(len(data))
                ))
        
        # Enum constraint
        if "enum" in schema:
            if data not in schema["enum"]:
                self.errors.append(ValidationError(
                    path, f"Value not in allowed enum values: {schema['enum']}",
                    str(schema["enum"]), str(data)
                ))

class JSONDataValidator:
    def __init__(self):
        self.schemas = {}
        self.validation_results = []
    
    def load_schema_from_file(self, schema_file: str, schema_name: str = None) -> bool:
        """Load schema from JSON file"""
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            name = schema_name or Path(schema_file).stem
            self.schemas[name] = JSONSchema(schema_data)
            return True
            
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error loading schema from {schema_file}: {e}")
            return False
    
    def add_schema(self, schema_name: str, schema_dict: Dict) -> bool:
        """Add schema from dictionary"""
        try:
            self.schemas[schema_name] = JSONSchema(schema_dict)
            return True
        except Exception as e:
            print(f"Error adding schema {schema_name}: {e}")
            return False
    
    def validate_file(self, json_file: str, schema_name: str) -> Tuple[bool, List[ValidationError]]:
        """Validate JSON file against schema"""
        if schema_name not in self.schemas:
            error = ValidationError("", f"Schema '{schema_name}' not found")
            return False, [error]
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.validate_data(data, schema_name)
            
        except FileNotFoundError:
            error = ValidationError("", f"File '{json_file}' not found")
            return False, [error]
        except json.JSONDecodeError as e:
            error = ValidationError("", f"Invalid JSON in file '{json_file}': {e}")
            return False, [error]
        except Exception as e:
            error = ValidationError("", f"Error reading file '{json_file}': {e}")
            return False, [error]
    
    def validate_data(self, data: Any, schema_name: str) -> Tuple[bool, List[ValidationError]]:
        """Validate data against schema"""
        if schema_name not in self.schemas:
            error = ValidationError("", f"Schema '{schema_name}' not found")
            return False, [error]
        
        schema = self.schemas[schema_name]
        is_valid, errors = schema.validate(data)
        
        # Store result
        result = {
            'timestamp': datetime.now().isoformat(),
            'schema_name': schema_name,
            'is_valid': is_valid,
            'error_count': len(errors),
            'errors': [str(error) for error in errors]
        }
        self.validation_results.append(result)
        
        return is_valid, errors
    
    def validate_json_string(self, json_string: str, schema_name: str) -> Tuple[bool, List[ValidationError]]:
        """Validate JSON string against schema"""
        try:
            data = json.loads(json_string)
            return self.validate_data(data, schema_name)
        except json.JSONDecodeError as e:
            error = ValidationError("", f"Invalid JSON string: {e}")
            return False, [error]
    
    def batch_validate(self, file_pattern: str, schema_name: str) -> Dict[str, Tuple[bool, List[ValidationError]]]:
        """Validate multiple files matching pattern"""
        from glob import glob
        
        results = {}
        files = glob(file_pattern)
        
        if not files:
            print(f"No files found matching pattern: {file_pattern}")
            return results
        
        for file_path in files:
            print(f"Validating {file_path}...")
            is_valid, errors = self.validate_file(file_path, schema_name)
            results[file_path] = (is_valid, errors)
        
        return results
    
    def get_schema_info(self, schema_name: str) -> Optional[Dict]:
        """Get information about a schema"""
        if schema_name not in self.schemas:
            return None
        
        schema = self.schemas[schema_name].schema
        
        def analyze_schema(schema_part):
            info = {}
            if "type" in schema_part:
                info["type"] = schema_part["type"]
            if "required" in schema_part:
                info["required_fields"] = schema_part["required"]
            if "properties" in schema_part:
                info["properties"] = {
                    prop: analyze_schema(prop_schema) 
                    for prop, prop_schema in schema_part["properties"].items()
                }
            return info
        
        return analyze_schema(schema)
    
    def create_sample_data(self, schema_name: str) -> Optional[Dict]:
        """Create sample data that conforms to schema"""
        if schema_name not in self.schemas:
            return None
        
        schema = self.schemas[schema_name].schema
        
        def generate_sample(schema_part):
            if "type" not in schema_part:
                return None
            
            data_type = schema_part["type"]
            
            if data_type == "string":
                if "enum" in schema_part:
                    return schema_part["enum"][0]
                return "sample_string"
            elif data_type == "number":
                return 42.0
            elif data_type == "integer":
                return 42
            elif data_type == "boolean":
                return True
            elif data_type == "array":
                if "items" in schema_part:
                    return [generate_sample(schema_part["items"])]
                return []
            elif data_type == "object":
                obj = {}
                if "properties" in schema_part:
                    for prop, prop_schema in schema_part["properties"].items():
                        obj[prop] = generate_sample(prop_schema)
                return obj
            elif data_type == "null":
                return None
            
            return None
        
        return generate_sample(schema)
    
    def export_validation_report(self, filename: str):
        """Export validation results to file"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'total_validations': len(self.validation_results),
                'successful_validations': sum(1 for r in self.validation_results if r['is_valid']),
                'failed_validations': sum(1 for r in self.validation_results if not r['is_valid']),
                'results': self.validation_results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            print(f"Validation report exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting report: {e}")
    
    def get_validation_statistics(self) -> Dict:
        """Get statistics about validation results"""
        if not self.validation_results:
            return {}
        
        total = len(self.validation_results)
        successful = sum(1 for r in self.validation_results if r['is_valid'])
        failed = total - successful
        
        # Schema usage
        schema_usage = {}
        for result in self.validation_results:
            schema = result['schema_name']
            schema_usage[schema] = schema_usage.get(schema, 0) + 1
        
        # Most common errors
        all_errors = []
        for result in self.validation_results:
            all_errors.extend(result['errors'])
        
        return {
            'total_validations': total,
            'successful_validations': successful,
            'failed_validations': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'schema_usage': schema_usage,
            'total_errors': len(all_errors),
            'loaded_schemas': list(self.schemas.keys())
        }

def create_sample_schemas():
    """Create some sample schemas for demonstration"""
    schemas = {
        "user": {
            "type": "object",
            "required": ["name", "email", "age"],
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 50
                },
                "email": {
                    "type": "string",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                "age": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 150
                },
                "phone": {
                    "type": "string",
                    "pattern": r"^\+?[\d\s\-\(\)]+$"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "pending"]
                }
            }
        },
        "product": {
            "type": "object",
            "required": ["name", "price", "category"],
            "properties": {
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100
                },
                "price": {
                    "type": "number",
                    "minimum": 0
                },
                "category": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "books", "home", "sports"]
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 10
                },
                "in_stock": {
                    "type": "boolean"
                }
            }
        },
        "config": {
            "type": "object",
            "required": ["app_name", "version"],
            "properties": {
                "app_name": {
                    "type": "string",
                    "minLength": 1
                },
                "version": {
                    "type": "string",
                    "pattern": r"^\d+\.\d+\.\d+$"
                },
                "debug": {
                    "type": "boolean"
                },
                "features": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "database": {
                    "type": "object",
                    "required": ["host", "port"],
                    "properties": {
                        "host": {
                            "type": "string"
                        },
                        "port": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 65535
                        },
                        "name": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
    return schemas

def main():
    """Main function to run the JSON data validator"""
    validator = JSONDataValidator()
    
    # Load sample schemas
    sample_schemas = create_sample_schemas()
    for name, schema in sample_schemas.items():
        validator.add_schema(name, schema)
    
    while True:
        print("\n=== JSON Data Validator ===")
        print("1. Validate JSON file")
        print("2. Validate JSON string")
        print("3. Batch validate files")
        print("4. Load schema from file")
        print("5. Add schema manually")
        print("6. View schema info")
        print("7. Generate sample data")
        print("8. View validation statistics")
        print("9. Export validation report")
        print("10. List available schemas")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                json_file = input("Enter JSON file path: ").strip()
                print("\nAvailable schemas:")
                for schema_name in validator.schemas.keys():
                    print(f"  • {schema_name}")
                
                schema_name = input("Enter schema name: ").strip()
                
                if schema_name in validator.schemas:
                    is_valid, errors = validator.validate_file(json_file, schema_name)
                    
                    if is_valid:
                        print("✅ Validation successful!")
                    else:
                        print("❌ Validation failed!")
                        print(f"Found {len(errors)} errors:")
                        for error in errors:
                            print(f"  • {error}")
                else:
                    print("Schema not found!")
            
            elif choice == '2':
                print("Enter JSON string (end with empty line):")
                json_lines = []
                while True:
                    line = input()
                    if line.strip() == "":
                        break
                    json_lines.append(line)
                
                json_string = '\n'.join(json_lines)
                
                print("\nAvailable schemas:")
                for schema_name in validator.schemas.keys():
                    print(f"  • {schema_name}")
                
                schema_name = input("Enter schema name: ").strip()
                
                if schema_name in validator.schemas:
                    is_valid, errors = validator.validate_json_string(json_string, schema_name)
                    
                    if is_valid:
                        print("✅ Validation successful!")
                    else:
                        print("❌ Validation failed!")
                        print(f"Found {len(errors)} errors:")
                        for error in errors:
                            print(f"  • {error}")
                else:
                    print("Schema not found!")
            
            elif choice == '3':
                file_pattern = input("Enter file pattern (e.g., *.json, data/*.json): ").strip()
                
                print("\nAvailable schemas:")
                for schema_name in validator.schemas.keys():
                    print(f"  • {schema_name}")
                
                schema_name = input("Enter schema name: ").strip()
                
                if schema_name in validator.schemas:
                    results = validator.batch_validate(file_pattern, schema_name)
                    
                    print(f"\nBatch validation results:")
                    for file_path, (is_valid, errors) in results.items():
                        status = "✅" if is_valid else "❌"
                        print(f"{status} {file_path}: {len(errors)} errors")
                        if errors and len(errors) <= 3:  # Show first few errors
                            for error in errors[:3]:
                                print(f"    • {error}")
                else:
                    print("Schema not found!")
            
            elif choice == '4':
                schema_file = input("Enter schema file path: ").strip()
                schema_name = input("Enter schema name (optional): ").strip()
                
                if validator.load_schema_from_file(schema_file, schema_name or None):
                    print("Schema loaded successfully!")
                else:
                    print("Failed to load schema.")
            
            elif choice == '5':
                schema_name = input("Enter schema name: ").strip()
                print("Enter schema JSON (end with empty line):")
                schema_lines = []
                while True:
                    line = input()
                    if line.strip() == "":
                        break
                    schema_lines.append(line)
                
                schema_string = '\n'.join(schema_lines)
                
                try:
                    schema_dict = json.loads(schema_string)
                    if validator.add_schema(schema_name, schema_dict):
                        print("Schema added successfully!")
                    else:
                        print("Failed to add schema.")
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON schema: {e}")
            
            elif choice == '6':
                print("\nAvailable schemas:")
                for schema_name in validator.schemas.keys():
                    print(f"  • {schema_name}")
                
                schema_name = input("Enter schema name: ").strip()
                
                info = validator.get_schema_info(schema_name)
                if info:
                    print(f"\nSchema '{schema_name}' information:")
                    print(json.dumps(info, indent=2))
                else:
                    print("Schema not found!")
            
            elif choice == '7':
                print("\nAvailable schemas:")
                for schema_name in validator.schemas.keys():
                    print(f"  • {schema_name}")
                
                schema_name = input("Enter schema name: ").strip()
                
                sample_data = validator.create_sample_data(schema_name)
                if sample_data is not None:
                    print(f"\nSample data for '{schema_name}' schema:")
                    print(json.dumps(sample_data, indent=2))
                else:
                    print("Schema not found or couldn't generate sample data!")
            
            elif choice == '8':
                stats = validator.get_validation_statistics()
                if stats:
                    print("\n=== Validation Statistics ===")
                    print(f"Total validations: {stats['total_validations']}")
                    print(f"Successful: {stats['successful_validations']}")
                    print(f"Failed: {stats['failed_validations']}")
                    print(f"Success rate: {stats['success_rate']:.1f}%")
                    print(f"Total errors: {stats['total_errors']}")
                    
                    if stats['schema_usage']:
                        print("\nSchema usage:")
                        for schema, count in stats['schema_usage'].items():
                            print(f"  {schema}: {count} validations")
                    
                    print(f"\nLoaded schemas: {', '.join(stats['loaded_schemas'])}")
                else:
                    print("No validation statistics available.")
            
            elif choice == '9':
                filename = input("Enter report filename (e.g., validation_report.json): ").strip()
                if not filename:
                    filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                validator.export_validation_report(filename)
            
            elif choice == '10':
                print("\nAvailable schemas:")
                if validator.schemas:
                    for schema_name in validator.schemas.keys():
                        schema_info = validator.get_schema_info(schema_name)
                        schema_type = schema_info.get('type', 'unknown') if schema_info else 'unknown'
                        print(f"  • {schema_name} (type: {schema_type})")
                else:
                    print("  No schemas loaded.")
            
            elif choice == '0':
                print("Thank you for using JSON Data Validator!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
