from django.db import models

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
