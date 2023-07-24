import Kizdar_data as kd

kizdar = kd.Kizdar_data('https://kiz0dar-fyj.net/', test=False, hideBrouser=True)
kizdar.get_date(start_page=1, end_page=20)
kizdar.saving_data()
# kizdar.saving_data('csv')