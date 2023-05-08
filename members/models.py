from django.db import models
from django.forms import ModelForm
from django import forms

SUBSCRIPTION_TYPE_CHOICES = (
    ('gym', 'Gym'),
    ('cross_fit', 'Cross Fit'),
    ('gym_and_cross_fit', 'Gym + Cross Fit'),
    ('pt', 'Personal Training')
)

SUBSCRIPTION_PERIOD_CHOICES = (
    ('1', '1 tháng'),
    ('2', '2 tháng'),
    ('3', '3 tháng'),
    ('4', '4 tháng'), 
    ('5', '5 tháng'),
    ('6', '6 tháng'),
    ('7', '7 tháng'),
    ('8', '8 tháng'),
    ('9', '9 tháng'),
    ('10', '10 tháng'),
    ('11', '11 tháng'),
    ('12', '12 tháng'),
)

FEE_STATUS = (
    ('paid', 'Đã thanh toán'),
    ('pending', 'Chưa thanh toán'),
)

STATUS = (
    (0, 'Đang hoạt động'),
    (1, 'Đã ngừng tham gia'),
)


class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(('Tên'), max_length=50)
    last_name = models.CharField(('Họ'), max_length=50)
    mobile_number = models.CharField(
        ('Mobile Number'), max_length=10, unique=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(('Địa chỉ'),max_length=300, blank=True)
    admitted_on = models.DateField(auto_now_add=True)
    registration_date = models.DateField(
        ('Ngày đăng kí'), default='dd/mm/yyyy')
    registration_upto = models.DateField(('Hạn đăng kí'))
    dob = models.DateField(('Ngày sinh'),default='dd/mm/yyyy')
    subscription_type = models.CharField(
        ('Khóa đăng kí'),
        max_length=30,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default=SUBSCRIPTION_TYPE_CHOICES[0][0]
    )
    subscription_period = models.CharField(
        ('Thời gian đăng kí'),
        max_length=30,
        choices=SUBSCRIPTION_PERIOD_CHOICES,
        default=SUBSCRIPTION_PERIOD_CHOICES[0][0]
    )
    amount = models.CharField(('Số tiền nộp'),max_length=30)
    fee_status = models.CharField(
        ('Trạng thái nộp tiền'),
        max_length=30,
        choices=FEE_STATUS,
        default=FEE_STATUS[0][0]
    )

    notification = models.IntegerField(default=2, blank=True)
    stop = models.IntegerField(
        ('Trạng thái hoạt động'), choices=STATUS, default=STATUS[0][0], blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class AddMemberForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddMemberForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].error_messages = {'required': 'Please enter first name'}
        self.fields['last_name'].error_messages = {'required': 'Please enter last name'}

    class Meta:
        model = Member
        # fields = ['first_name', 'last_name', 'mobile_number', 'email', 'address', 'subscription_type', 'subscription_period', 'amount']
        fields = '__all__'
        # registration_upto will be excluded from the form
        exclude = ['registration_upto']
        # specify the different type of input such as a date picker, text area, or file upload field. fields
        widgets = {
        'registration_date': forms.DateInput(attrs={'class': 'datepicker form-control', 'type': 'date'}),
        'address': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        'medical_history': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        'dob': forms.DateInput(attrs={'class': 'datepicker form-control', 'type': 'date'}),
        'photo': forms.FileInput(attrs={'accept': 'image/*;capture=camera'})
        }

    def clean_mobile_number(self, *args, **kwargs):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number.isdigit():
            raise forms.ValidationError('Mobile number should be a number')
        if Member.objects.filter(mobile_number=mobile_number).exists():
            raise forms.ValidationError('This mobile number has already been registered.')
        else:
            if len(str(mobile_number)) == 10:
                return mobile_number
            else:
                raise forms.ValidationError('Mobile number should be 10 digits long.')
        return mobile_number

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount.isdigit():
            raise forms.ValidationError('Amount should be a number')
        return amount

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('dob')
        first_name = cleaned_data.get('first_name').capitalize()
        last_name = cleaned_data.get('last_name').capitalize()
        queryset = Member.objects.filter(
                        first_name=first_name,
                        last_name=last_name,
                        dob=dob
                    ).count()
        if queryset > 0:
            raise forms.ValidationError('This member already exists!')


class SearchForm(forms.Form):
    search = forms.CharField(label='Tìm kiếm', max_length=100, required=False)

    def clean_search(self, *args, **kwargs):
        search = self.cleaned_data.get('search')
        if search == '':
            raise forms.ValidationError('Please enter a name in search box')
        return search