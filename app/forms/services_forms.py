from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, SubmitField, TelField
from wtforms.validators import DataRequired, NumberRange, Length


class CBCTransferForm(FlaskForm):
    """Transfer to another CBC bank account."""
    recipient_account = StringField('CBC Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20, message='Account number must be 8-20 characters')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0, message='Amount must be between 1.00 and 500,000.00 Birr')
    ])
    description = StringField('Remark', default='CBC Transfer', validators=[Length(max=100)])
    submit = SubmitField('Transfer to CBC Account')


class BeneficiaryForm(FlaskForm):
    """Add / manage beneficiary."""
    name = StringField('Beneficiary Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    account_number = StringField('Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    bank_name = SelectField('Bank', choices=[
        ('CBC Bank', 'CBC Bank'),
        ('Awash Bank', 'Awash Bank'),
        ('Dashen Bank', 'Dashen Bank'),
        ('Bank of Abyssinia', 'Bank of Abyssinia'),
        ('Wegagen Bank', 'Wegagen Bank'),
        ('Other', 'Other Bank')
    ], default='CBC Bank')
    submit = SubmitField('Save Beneficiary')


class OwnAccountTransferForm(FlaskForm):
    """Transfer between own accounts."""
    from_account = SelectField('From Account', coerce=int, validators=[DataRequired()])
    to_account = SelectField('To Account', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0)
    ])
    description = StringField('Remark', default='Own Account Transfer', validators=[Length(max=100)])
    submit = SubmitField('Transfer Between Accounts')


class CBCCashOutForm(FlaskForm):
    """CBC Cash-out via code (agent banking)."""
    phone_number = StringField('Receiver Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15, message='Enter a valid phone number')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=10.0, max=25000.0, message='Amount must be between 10 and 25,000 Birr')
    ])
    submit = SubmitField('Generate Cash-Out Code')


class ATMCashOutForm(FlaskForm):
    """Cardless ATM cash-out."""
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=100.0, max=10000.0, message='ATM cash-out: 100 - 10,000 Birr')
    ])
    submit = SubmitField('Generate ATM Code')


class OtherBankTransferForm(FlaskForm):
    """Transfer to another bank."""
    bank_name = SelectField('Destination Bank', choices=[
        ('Awash Bank', 'Awash Bank'),
        ('Dashen Bank', 'Dashen Bank'),
        ('Bank of Abyssinia', 'Bank of Abyssinia'),
        ('Wegagen Bank', 'Wegagen Bank'),
        ('Nib International Bank', 'Nib International Bank'),
        ('Cooperative Bank of Oromia', 'Cooperative Bank of Oromia'),
        ('Bunna Bank', 'Bunna Bank'),
        ('Zemen Bank', 'Zemen Bank'),
    ], validators=[DataRequired()])
    recipient_account = StringField('Recipient Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    recipient_name = StringField('Recipient Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=200000.0)
    ])
    description = StringField('Remark', default='Inter-Bank Transfer', validators=[Length(max=100)])
    submit = SubmitField('Send to Other Bank')


class AirtimeForm(FlaskForm):
    """Top-up airtime for mobile."""
    provider = SelectField('Service Provider', choices=[
        ('Ethio Telecom', 'Ethio Telecom'),
        ('Safaricom Ethiopia', 'Safaricom Ethiopia'),
    ], default='Ethio Telecom', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15, message='Enter a valid phone number')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=5.0, max=5000.0, message='Airtime: 5 - 5,000 Birr')
    ])
    submit = SubmitField('Buy Airtime')


class BillsUtilitiesForm(FlaskForm):
    """Pay utility bills (electricity, water, telecoms, internet)."""
    biller_category = SelectField('Biller / Utility Type', choices=[
        ('Ethiopian Electric Utility (EEU)', 'Ethiopian Electric Utility (EEU)'),
        ('Addis Ababa Water & Sewerage Authority (AAWSA)', 'Addis Ababa Water & Sewerage (AAWSA)'),
        ('Ethio Telecom Postpaid Bill', 'Ethio Telecom Postpaid / Bill'),
        ('Safaricom Postpaid Bill', 'Safaricom Postpaid Bill'),
        ('Broadband Fiber Internet', 'Broadband / Fiber Internet'),
        ('City Waste & Sanitation', 'City Waste & Sanitation'),
    ], default='Ethiopian Electric Utility (EEU)', validators=[DataRequired()])
    bill_reference = StringField('Customer / Contract / Meter No.', validators=[
        DataRequired(),
        Length(min=4, max=30, message='Enter a valid contract or meter number')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0, message='Amount must be between 1.00 and 500,000.00 Birr')
    ])
    description = StringField('Remark', default='Utility Bill Payment', validators=[Length(max=100)])
    submit = SubmitField('Pay Bill')


class TravelForm(FlaskForm):
    """Pay for flights, ride hailing, bus and train tickets."""
    travel_type = SelectField('Travel Provider', choices=[
        ('Ethiopian Airlines', 'Ethiopian Airlines (Flight Ticket)'),
        ('Feres / Ride Taxi', 'Feres / Ride (Taxi / Ride Hailing)'),
        ('Selam Bus / Sky Bus', 'Cross-Country Bus (Selam / Sky Bus)'),
        ('Ethio-Djibouti Railway', 'Ethio-Djibouti Railway (Train)'),
        ('Hotel & Lodging', 'Hotel & Accommodation Booking'),
    ], default='Ethiopian Airlines', validators=[DataRequired()])
    booking_reference = StringField('Booking Reference / Ticket / PNR', validators=[
        DataRequired(),
        Length(min=3, max=30, message='Enter a valid booking reference or ticket ID')
    ])
    passenger_name = StringField('Passenger / Customer Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=5.0, max=1000000.0, message='Amount must be between 5.00 and 1,000,000.00 Birr')
    ])
    description = StringField('Remark', default='Travel Booking', validators=[Length(max=100)])
    submit = SubmitField('Pay for Travel')


class ShoppingForm(FlaskForm):
    """Pay at merchant store or online shopping."""
    merchant_type = SelectField('Merchant Category', choices=[
        ('Supermarket & Grocery', 'Supermarket & Grocery'),
        ('E-commerce & Online Shopping', 'E-commerce & Online Shopping'),
        ('Electronics & Appliances', 'Electronics & Appliances'),
        ('Pharmacy & Healthcare', 'Pharmacy & Healthcare'),
        ('Fashion & Apparel', 'Fashion & Clothing'),
        ('Restaurant & Cafe', 'Restaurant & Cafe'),
    ], default='Supermarket & Grocery', validators=[DataRequired()])
    merchant_code = StringField('Merchant Code / Till Number', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Enter a valid merchant code or till number')
    ])
    invoice_number = StringField('Invoice / Order Number', validators=[
        DataRequired(),
        Length(min=2, max=30, message='Enter invoice or order ID')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0, message='Amount must be between 1.00 and 500,000.00 Birr')
    ])
    description = StringField('Remark', default='Shopping Payment', validators=[Length(max=100)])
    submit = SubmitField('Confirm & Pay')


class GovernmentServicesForm(FlaskForm):
    """Pay for government services and official fees."""
    agency = SelectField('Government Agency / Service', choices=[
        ('Immigration & Citizenship Service (ICS)', 'ICS (Passport & Visa Fees)'),
        ('Document Authentication & Registration (DARA)', 'DARA (Document Authentication)'),
        ('Traffic Management Agency', 'Traffic Penalty & Fine Payment'),
        ('Vital Events Registration Agency', 'Vital Events (Birth/Marriage Certificate)'),
        ('City Administration Land & Housing', 'Municipal Land & Property Services'),
        ('Trade & Industry Bureau', 'Commercial Registration & Trade License'),
    ], default='Immigration & Citizenship Service (ICS)', validators=[DataRequired()])
    application_number = StringField('Application / Order / Notice ID', validators=[
        DataRequired(),
        Length(min=4, max=30, message='Enter a valid application or notice number')
    ])
    applicant_name = StringField('Applicant Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    amount = DecimalField('Fee Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=1000000.0, message='Fee must be between 1.00 and 1,000,000.00 Birr')
    ])
    description = StringField('Remark', default='Government Service Fee', validators=[Length(max=100)])
    submit = SubmitField('Pay Government Fee')


class SubscriptionsForm(FlaskForm):
    """Pay for entertainment and media subscriptions."""
    subscription_service = SelectField('Service Provider', choices=[
        ('DSTV Ethiopia', 'DSTV Ethiopia (Multichoice)'),
        ('Canal+ Ethiopia', 'Canal+ Ethiopia'),
        ('Netflix Gift Voucher', 'Netflix Voucher'),
        ('Spotify / Music Service', 'Spotify / Music Streaming'),
        ('Gym & Fitness Membership', 'Gym & Fitness Membership'),
        ('Software & Cloud Services', 'Software / Cloud Hosting'),
    ], default='DSTV Ethiopia', validators=[DataRequired()])
    account_number = StringField('Smartcard / Account Number', validators=[
        DataRequired(),
        Length(min=4, max=30, message='Enter a valid smartcard or account number')
    ])
    package = SelectField('Subscription Package', choices=[
        ('Standard Monthly Package', 'Standard Monthly Package'),
        ('Premium Monthly Package', 'Premium Monthly Package'),
        ('Family Entertainment Package', 'Family Entertainment Package'),
        ('Sports Bouquet', 'Sports Bouquet'),
        ('Annual Subscription', 'Annual Subscription (12 Months)'),
    ], default='Standard Monthly Package')
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=50.0, max=100000.0, message='Subscription amount must be between 50.00 and 100,000.00 Birr')
    ])
    description = StringField('Remark', default='Subscription Renewal', validators=[Length(max=100)])
    submit = SubmitField('Renew Subscription')


class PayForForm(FlaskForm):
    """General Pay For (schools, medical, services, paybill)."""
    category = SelectField('Pay For Category', choices=[
        ('School & University Tuition', 'School & University Tuition'),
        ('Hospital & Healthcare Clinic', 'Hospital & Healthcare Clinic'),
        ('Fuel & Service Station', 'Fuel & Service Station'),
        ('Event / Concert / Cinema', 'Event / Concert / Cinema Ticket'),
        ('Professional & Legal Fees', 'Professional & Consulting Fees'),
        ('General Paybill / Till', 'General Paybill / Merchant Till'),
    ], default='School & University Tuition', validators=[DataRequired()])
    paybill_number = StringField('Paybill / Short Code', validators=[
        DataRequired(),
        Length(min=4, max=25, message='Enter a valid short code or account number')
    ])
    reference_number = StringField('Student ID / Patient ID / Ref', validators=[
        DataRequired(),
        Length(min=2, max=30, message='Enter reference identifier')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0, message='Amount must be between 1.00 and 500,000.00 Birr')
    ])
    description = StringField('Remark', default='Payment For Goods / Services', validators=[Length(max=100)])
    submit = SubmitField('Send Payment')


class DonationForm(FlaskForm):
    """Charitable donations and non-profit support."""
    charity_name = SelectField('Charity / Organization', choices=[
        ('Mekedonia Home for Elderly and Mentally Disabled', 'Mekedonia (Elderly & Mentally Disabled)'),
        ('Ethiopian Red Cross Society', 'Ethiopian Red Cross Society'),
        ('Gergesenon Mental Health Rehabilitation', 'Gergesenon Rehabilitation Center'),
        ('Muday Association', 'Muday Association (Women & Children)'),
        ('National Emergency & Disaster Relief Fund', 'National Emergency Relief Fund'),
        ('Community Religious & Heritage Fund', 'Community Religious & Heritage Fund'),
    ], default='Mekedonia Home for Elderly and Mentally Disabled', validators=[DataRequired()])
    cause = StringField('Campaign / Purpose', default='General Humanitarian Support', validators=[Length(max=100)])
    donor_name = StringField('Donor Display Name', default='Anonymous Donor', validators=[Length(max=100)])
    amount = DecimalField('Donation Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=5.0, max=1000000.0, message='Donation must be at least 5.00 Birr')
    ])
    submit = SubmitField('Donate Now')


class TaxPaymentForm(FlaskForm):
    """Ministry of Revenues and municipal tax payments."""
    tax_type = SelectField('Tax Type', choices=[
        ('Ministry of Revenues (MOR) - Business Income Tax', 'Business Income Tax (Category A/B/C)'),
        ('Personal Income Tax (Employment PIT)', 'Personal Income Tax (Employment PIT)'),
        ('Value Added Tax (VAT)', 'Value Added Tax (VAT)'),
        ('Customs Duty & Import Tariff', 'Customs Duty & Import Tariff'),
        ('Withholding Tax', 'Withholding Tax'),
        ('City Administration Property Tax', 'City Property / Land Use Tax'),
    ], default='Ministry of Revenues (MOR) - Business Income Tax', validators=[DataRequired()])
    tin_number = StringField('Taxpayer Identification Number (TIN)', validators=[
        DataRequired(),
        Length(min=8, max=15, message='Enter a valid 10-digit TIN number')
    ])
    assessment_number = StringField('Assessment / Document / Declaration No.', validators=[
        DataRequired(),
        Length(min=4, max=30, message='Enter assessment or document reference number')
    ])
    amount = DecimalField('Tax Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=5000000.0, message='Amount must be between 1.00 and 5,000,000.00 Birr')
    ])
    description = StringField('Remark', default='Government Tax Settlement', validators=[Length(max=100)])
    submit = SubmitField('Pay Tax')


class MyServiceForm(FlaskForm):
    """Personalized and saved custom services."""
    service_name = StringField('Service Name', validators=[
        DataRequired(),
        Length(min=2, max=60, message='Enter a descriptive service name')
    ])
    service_provider = StringField('Provider / Company', validators=[
        DataRequired(),
        Length(min=2, max=60)
    ])
    account_reference = StringField('Account / Reference Number', validators=[
        DataRequired(),
        Length(min=3, max=30)
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0, message='Amount must be between 1.00 and 500,000.00 Birr')
    ])
    description = StringField('Remark', default='Custom Service Payment', validators=[Length(max=100)])
    save_favorite = SelectField('Save to My Quick Favorites?', choices=[
        ('yes', 'Yes, save to my frequent shortcuts'),
        ('no', 'No, one-time payment')
    ], default='yes')
    submit = SubmitField('Submit Service Payment')

