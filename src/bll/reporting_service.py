from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import logging
from decimal import Decimal
from sqlalchemy.orm import Session

# Optional reportlab imports with proper error handling
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Local imports
from src.services.sales_service import SalesService
from src.services.expense_service import ExpenseService
from src.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


def validate_date(date_str: str) -> tuple[bool, Optional[str]]:
    """Validate date string format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"


class ReportingService:
    def __init__(self, session: Session):
        self.session = session
        self.sales_service = SalesService(session)
        self.expense_service = ExpenseService(session)
        self.inventory_service = InventoryService(session)

    def generate_daily_report(self, target_date: str) -> Dict:
        """Generate comprehensive daily report"""
        try:
            # Validate date
            date_valid, date_error = validate_date(target_date)
            if not date_valid:
                raise ValueError(date_error)

            # Get sales summary
            sales_summary = self.sales_service.get_daily_sales_summary(target_date)

            # Get expense summary
            expense_summary = self.expense_service.get_expense_summary(
                target_date, target_date
            )

            # Get inventory status
            inventory_status = self.inventory_service.get_inventory_status()

            # Calculate net income
            total_sales = sales_summary['summary']['total_sales']
            total_expenses = expense_summary['summary']['total_amount']
            net_income = total_sales - total_expenses

            return {
                'date': target_date,
                'overview': {
                    'total_sales': total_sales,
                    'total_expenses': total_expenses,
                    'net_income': net_income,
                    'transaction_count': sales_summary['summary']['transaction_count']
                },
                'sales': {
                    'by_hour': sales_summary['hourly_sales'],
                    'by_payment_method': sales_summary['payment_methods'],
                    'top_items': sales_summary['top_items']
                },
                'expenses': {
                    'by_category': expense_summary['by_category']
                },
                'inventory': {
                    'total_value': inventory_status['total_value'],
                    'alerts': inventory_status['alerts']
                },
                'staff_performance': sales_summary['staff_performance']
            }

        except Exception as e:
            logger.error(f"Failed to generate daily report: {str(e)}")
            raise

    def export_report(self, report_type: str, start_date: str,
                      end_date: str, format: str = 'pdf') -> bytes:
        """Export report in specified format"""
        try:
            if not REPORTLAB_AVAILABLE and format == 'pdf':
                raise ValueError("PDF export requires reportlab package")

            # Get report data based on type
            report_data = self._get_report_data(report_type, start_date, end_date)

            # Export based on format
            if format == 'pdf':
                return self._export_to_pdf(report_data, report_type)
            elif format == 'csv':
                return self._export_to_csv(report_data, report_type)
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            logger.error(f"Failed to export report: {str(e)}")
            raise

    def _get_report_data(self, report_type: str, start_date: str, end_date: str) -> Dict:
        """Get report data based on type"""
        if report_type == 'daily':
            return self.generate_daily_report(start_date)
        elif report_type == 'periodic':
            return self.generate_periodic_report(start_date, end_date)
        elif report_type == 'inventory':
            return self.generate_inventory_report()
        else:
            raise ValueError(f"Invalid report type: {report_type}")

    def _export_to_pdf(self, data: Dict, report_type: str) -> bytes:
        """Export report data to PDF format"""
        if not REPORTLAB_AVAILABLE:
            raise ValueError("PDF export requires reportlab package")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Add report content
        elements.extend(self._get_pdf_elements(data, report_type, styles))

        # Build PDF
        doc.build(elements)
        return buffer.getvalue()

    def _export_to_csv(self, data: Dict, report_type: str) -> bytes:
        """Export report data to CSV format"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write report data
        self._write_csv_data(writer, data, report_type)

        return output.getvalue().encode('utf-8')

    def _get_pdf_elements(self, data: Dict, report_type: str, styles) -> List:
        """Generate PDF elements based on report type"""
        elements = []

        # Add title
        title = f"Brew and Bite Café - {report_type.capitalize()} Report"
        elements.append(Paragraph(title, styles['Title']))

        # Add date
        elements.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))

        # Add report-specific content
        if report_type == 'daily':
            elements.extend(self._get_daily_report_elements(data, styles))
        elif report_type == 'periodic':
            elements.extend(self._get_periodic_report_elements(data, styles))
        elif report_type == 'inventory':
            elements.extend(self._get_inventory_report_elements(data, styles))

        return elements

    def _write_csv_data(self, writer, data: Dict, report_type: str):
        """Write CSV data based on report type"""
        if report_type == 'daily':
            self._write_daily_report_csv(writer, data)
        elif report_type == 'periodic':
            self._write_periodic_report_csv(writer, data)
        elif report_type == 'inventory':
            self._write_inventory_report_csv(writer, data)

    def get_recent_activities(self, limit: int = 50) -> List[Dict]:
        """Get recent activities for dashboard"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            activities = []

            # Get recent sales
            sales = self.sales_service.get_sales_by_date_range(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )

            # Get recent expenses
            expenses = self.expense_service.get_expenses_by_date_range(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )

            # Combine and process activities
            for sale in sales:
                activities.append({
                    'timestamp': sale['date'],
                    'type': 'SALE',
                    'amount': sale['total_amount'],
                    'details': f"Sale #{sale['id']} - {len(sale['items'])} items"
                })

            for expense in expenses:
                activities.append({
                    'timestamp': expense['date'],
                    'type': 'EXPENSE',
                    'amount': expense['amount'],
                    'details': f"{expense['category']} - {expense['description']}"
                })

            # Sort by timestamp and limit results
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:limit]

        except Exception as e:
            logger.error(f"Failed to get recent activities: {str(e)}")
            raise