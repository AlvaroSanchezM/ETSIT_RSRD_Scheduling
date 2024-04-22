class Zone:
    def __init__(self, name, users, bps_per_hz, r_peak_mbps, r_sla_mbps):
        self.name = name
        self.users = users
        self.bps_per_hz = bps_per_hz
        self.r_peak_mbps = r_peak_mbps
        self.r_sla_mbps = r_sla_mbps

    def __repr__(self):
        return f"Zone('{self.name}', {self.users}, {self.bps_per_hz}, {self.r_peak_mbps}, {self.r_sla_mbps})"

    def __lt__(self, other):
        return self.bps_per_hz > other.bps_per_hz
    
class Scenario:
    def __init__(self, b_total_MHz, zones):
        self.b_total_MHz = b_total_MHz
        self.b_remain_MHz = b_total_MHz
        self.zones = sorted(zones)
        print(self.zones)
    
    def computeZoneBps(self, zone):
        return zone.users * zone.bps_per_hz * self.b_total_MHz
    
    def computeZone(self, zone):
        n_users = zone.users
        ro_bpsHz = zone.bps_per_hz
        b_total = n_users * zone.r_peak_mbps / zone.bps_per_hz
        if b_total >= self.b_remain_MHz:
            b_total = self.b_remain_MHz
        b_user = b_total / n_users
        r_user = b_user * ro_bpsHz
        return b_total, r_user
    
    def maxCI(self):
        r_final = []
        for zone in self.zones:
            zone_name = zone.name
            b_total, r_user = self.computeZone(zone)
            self.b_remain_MHz -= b_total
            r_final.append([zone_name, r_user])
        return r_final
    
    def maxCI_MinRate(self):
        r_final = []
        # TODO: To Complete
         #Primero calcular users x (r_sla_Mbps / bps_per_hz) total para repartir la banda en un inicio
        requerido = 0
        for zone in self.zones:
            sla_Mhz_per_user = zone.r_sla_mbps/zone.bps_per_hz
            sla_Mhz_zone = zone.users * sla_Mhz_per_user
            requerido += sla_Mhz_zone
        print("Para dar a todos r_sla_mbps (igual para todos) se necesitan "+ str(requerido) + " Mbps")
        # Si se necesita más banda para cumplir la SLA que la que hay, se reparte a partes iguales la velocidad disponible
        if requerido > self.b_total_MHz:
            tot_us_bps_hz=0
            for zone in self.zones:
                us_bps_hz = zone.users * zone.bps_per_hz
                tot_us_bps_hz += us_bps_hz
            rfinal_per_user=self.b_total_MHz/tot_us_bps_hz
            for zone in self.zones:
                zone_name = zone.name
                r_user = rfinal_per_user
                r_final.append([zone_name, r_user])
            return r_final
        #si hay la justa para cumplir la sla en todas las zonas, se reparte a partes iguales de nuevo
        elif requerido == self.b_total_MHz:
            for zone in self.zones:
                zone_name = zone.name
                r_user = zone.r_sla_mbps
                r_final.append([zone_name, r_user])
            return r_final
        # Si hay de sobra para repartir un extra además de la usada para el SLA en todas las terminales,
        # se reparte a los que mejor la puedan usar con max CI
        else:
            self.b_remain_MHz = self.b_total_MHz - requerido
            aux_b_extra = self.b_remain_MHz
            
            for zone in self.zones:
                aux_r_peak_mbps = zone.r_peak_mbps - zone.r_sla_mbps
                zone_name = zone.name
                #-aux_b_extra, r_user = self.computeZone(zone)-
                n_users = zone.users
                ro_bpsHz = zone.bps_per_hz
                aux_b_extra = n_users * aux_r_peak_mbps / zone.bps_per_hz
                if aux_b_extra >= self.b_remain_MHz:
                    aux_b_extra = self.b_remain_MHz
                b_user = aux_b_extra / n_users
                r_user = b_user * ro_bpsHz + zone.r_sla_mbps
                #------------------------------------------
                self.b_remain_MHz -= aux_b_extra
                r_final.append([zone_name, r_user])
            return r_final
    
def main():
    r_peak_mbps = 3
    r_sla_mbps = 0.3
    zones = [
        Zone("Z4", 14 , 0.4, r_peak_mbps, r_sla_mbps),
        Zone("Z3", 19 , 1.5, r_peak_mbps, r_sla_mbps),
        Zone("Z2", 9 , 3, r_peak_mbps, r_sla_mbps),
        Zone("Z1", 8 , 4.5, r_peak_mbps, r_sla_mbps),
    ]
    scenario = Scenario(25, zones)
    r_final = scenario.maxCI()
    print("B[MHz] remaining:", scenario.b_remain_MHz)
    print("R[Mbps] final:", r_final)

    
if __name__ == "__main__":
    main()
