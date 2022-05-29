from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt
from treenipaivakirja.utils import coalesce, duration_to_decimal, speed_min_per_km
        
        
class Harjoitus(models.Model):
    pvm = models.DateField(verbose_name='Päivä')
    aika = models.ForeignKey('aika', on_delete=models.PROTECT, verbose_name='vvvvkkpp', blank=True)
    laji = models.ForeignKey('laji', on_delete=models.PROTECT, verbose_name='Laji')
    kesto = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    kesto_h = models.PositiveIntegerField(null=True, blank=True, verbose_name='h')
    kesto_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    matka = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (km/h)', blank=True)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (min/km)', blank=True)
    vauhti_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    vauhti_s = models.PositiveIntegerField(null=True, blank=True, verbose_name='s')
    keskisyke = models.IntegerField(null=True, blank=True)
    kalorit = models.IntegerField(null=True, blank=True)    
    tuntuma_choices = ((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10))    
    tuntuma = models.IntegerField(choices=tuntuma_choices,null=True, blank=True)
    kommentti = models.TextField(max_length=250, null=True, blank=True)
    vuorokaudenaika_choices = ((1,'aamupäivä'),(2,'iltapäivä'),)
    vuorokaudenaika = models.IntegerField(choices=vuorokaudenaika_choices, blank=False, default=2, verbose_name="")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nousu = models.IntegerField(null=True, blank=True, verbose_name='Nousu (m)')

    class Meta:
        verbose_name_plural = "Harjoitus"
    
    def save(self, *args, **kwargs):
        self.aika_id = self.pvm.strftime('%Y%m%d')
        self.kesto_h = coalesce(self.kesto_h,0)
        self.kesto_min = coalesce(self.kesto_min,0)
        self.kesto = duration_to_decimal(self.kesto_h,self.kesto_min)
        self.vauhti_min_km = speed_min_per_km(self.vauhti_min,self.vauhti_s)
        if self.vauhti_min_km is None and self.vauhti_km_h is not None and self.vauhti_km_h != 0:
            self.vauhti_min_km = 60 / self.vauhti_km_h
            self.vauhti_min = int(self.vauhti_min_km)
            self.vauhti_s = round((self.vauhti_min_km*60) % 60,0)
        elif self.vauhti_min_km is not None and self.vauhti_min_km != 0 and self.vauhti_km_h is None:
            self.vauhti_km_h = 60 / self.vauhti_min_km
        super(Harjoitus, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s h' % (self.laji, self.kesto)
    
    
class Laji(models.Model):   
    laji = models.CharField(max_length=10, verbose_name='Lyhenne')
    laji_nimi = models.CharField(max_length=50, verbose_name='Laji')
    laji_ryhma = models.CharField(max_length=50, verbose_name='Lajiryhmä', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Laji"
        ordering = ['laji_nimi']

    def __str__(self):
        return self.laji_nimi
         

class Aika(models.Model):
    vvvvkkpp = models.IntegerField(primary_key=True)
    pvm = models.DateField()
    vuosi = models.IntegerField(verbose_name='Vuosi')
    kk = models.IntegerField()
    kk_nimi = models.CharField(max_length=20)
    paiva = models.IntegerField()
    vko = models.IntegerField()
    viikonpaiva = models.IntegerField()
    viikonpaiva_lyh = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Aika" 

    def __str__(self):
        return str(self.vvvvkkpp)


class Teho(models.Model):
    harjoitus = models.ForeignKey('harjoitus', on_delete=models.CASCADE)
    nro = models.IntegerField(blank=False)
    kesto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    kesto_h = models.PositiveIntegerField(null=True, blank=True, verbose_name='h')
    kesto_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    keskisyke = models.IntegerField(null=True, blank=True)
    maksimisyke = models.IntegerField(null=True, blank=True, verbose_name='Maksimisyke')
    matka = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (km/h)', blank=True)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (min/km)', blank=True)
    vauhti_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    vauhti_s = models.PositiveIntegerField(null=True, blank=True, verbose_name='s')
    tehoalue = models.ForeignKey('tehoalue', on_delete=models.PROTECT, blank=False)

    class Meta:
        verbose_name_plural = "Teho"

    def save(self, *args, **kwargs):
        self.kesto_h = coalesce(self.kesto_h,0)
        self.kesto_min = coalesce(self.kesto_min,0)
        self.kesto = duration_to_decimal(self.kesto_h,self.kesto_min)
        self.vauhti_min_km = speed_min_per_km(self.vauhti_min,self.vauhti_s)
        if self.vauhti_min_km is not None and self.vauhti_min_km != 0:
            self.vauhti_km_h = 60 / self.vauhti_min_km
        super(Teho, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s h' % (self.harjoitus, self.tehoalue, self.kesto)


class Tehoalue(models.Model):
    jarj_nro = models.IntegerField(blank=False, verbose_name='Järj.Nro')
    tehoalue = models.CharField(max_length=100, verbose_name='Tehoalue')
    alaraja = models.IntegerField(null=True, blank=True, verbose_name='Alaraja')
    ylaraja = models.IntegerField(null=True, blank=True, verbose_name='Yläraja')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Tehoalue"
        ordering = ['jarj_nro']

    def __str__(self):
        return self.tehoalue


class Kausi(models.Model):
    kausi = models.CharField(max_length=20, verbose_name='Harjoituskausi')
    alkupvm = models.DateField(verbose_name='Alkupäivä')
    loppupvm = models.DateField(verbose_name='Loppupäivä')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Kausi"
        ordering = ['kausi']

    def __str__(self):
        return self.kausi


class PolarUser(models.Model):
    polar_user_id = models.BigIntegerField(primary_key=True)
    access_token = encrypt(models.CharField(max_length=500, null=True, blank=True))
    registration_date = models.DateTimeField(null=True, blank=True)
    latest_exercise_transaction_id = models.BigIntegerField(null=True, blank=True)
    latest_activity_transaction_id = models.BigIntegerField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) 

    def __str__(self):
        return str(self.polar_user_id)


class PolarSport(models.Model):
    polar_user = models.ForeignKey(PolarUser, on_delete=models.CASCADE)
    polar_sport = models.CharField(max_length=100, verbose_name='Polar laji')
    laji = models.ForeignKey(Laji, on_delete=models.CASCADE, verbose_name='Laji')

    def __str__(self):
        return str(self.polar_sport)

    class Meta:
        unique_together = [['polar_sport', 'polar_user']]


class PolarSleep(models.Model):
    polar_user = models.ForeignKey(PolarUser, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DecimalField(max_digits=4, decimal_places=2)
    continuity = models.DecimalField(max_digits=2, decimal_places=1)
    light_sleep = models.DecimalField(max_digits=4, decimal_places=2)
    deep_sleep = models.DecimalField(max_digits=4, decimal_places=2)
    rem_sleep = models.DecimalField(max_digits=4, decimal_places=2)
    sleep_score = models.IntegerField()
    total_interruption_duration = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        unique_together = [['polar_user', 'date']]


class PolarRecharge(models.Model):
    polar_user = models.ForeignKey(PolarUser, on_delete=models.CASCADE)
    date = models.DateField()
    heart_rate_avg = models.IntegerField()
    heart_rate_variability_avg = models.IntegerField()
    nightly_recharge_status = models.IntegerField()

    class Meta:
        unique_together = [['polar_user', 'date']]


class OuraUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = encrypt(models.CharField(max_length=500, null=True, blank=True))
    refresh_token = encrypt(models.CharField(max_length=500, null=True, blank=True))  

    def __str__(self):
        return str(self.user_id)


class OuraSleep(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    bedtime_start = models.DateTimeField()
    bedtime_end = models.DateTimeField()
    duration = models.DecimalField(max_digits=4, decimal_places=2)
    total = models.DecimalField(max_digits=4, decimal_places=2)
    awake = models.DecimalField(max_digits=4, decimal_places=2)
    rem = models.DecimalField(max_digits=4, decimal_places=2)
    deep = models.DecimalField(max_digits=4, decimal_places=2)
    light = models.DecimalField(max_digits=4, decimal_places=2)
    hr_min = models.IntegerField()
    hr_avg = models.DecimalField(max_digits=4, decimal_places=2)
    hrv_avg = models.IntegerField()
    score = models.IntegerField()

    class Meta:
        unique_together = [['user', 'date']]


class HarjoitusView(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    vuosi = models.IntegerField()
    kk = models.IntegerField()
    kk_nimi = models.CharField(max_length=20)
    vko = models.IntegerField()
    viikonpaiva = models.CharField(max_length=20)
    vvvvkkpp = models.IntegerField()
    pvm = models.DateField()
    vuorokaudenaika = models.IntegerField()
    laji = models.CharField(max_length=10)
    laji_nimi = models.CharField(max_length=50)
    laji_ryhma = models.CharField(max_length=50)
    kesto_h = models.IntegerField()
    kesto_min = models.IntegerField()
    kesto = models.DecimalField(max_digits=5, decimal_places=2)
    keskisyke = models.IntegerField()
    matka = models.DecimalField(max_digits=5, decimal_places=2)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2)
    kalorit = models.IntegerField()
    nousu = models.IntegerField()
    tuntuma = models.IntegerField()
    kommentti = models.CharField(max_length=250)
    kausi = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'treenipaivakirja_harjoitus_vw'
