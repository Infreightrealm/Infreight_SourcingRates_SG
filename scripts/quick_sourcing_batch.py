# -*- coding: utf-8 -*-
import sys
import os
import asyncio
import argparse
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from models.schemas import RateSearchRequest, ALL_CARRIERS, CarrierResultStatus
from carriers.registry import get_connector

DEFAULT_140_PORTS = [
    'GDYNIA', 'GDANSK', 'ANTWERP', 'BARCELONA', 'BURGAS', 'PIRAEUS', 'FELIXSTOWE', 'LEIXOES',
    'ROTTERDAM', 'HAMBURG', 'SOKHNA', 'KARACHI', 'NEW YORK', 'KOPER', 'LIVERPOOL', 'BRISTOL',
    'HOUSTON', 'CHITTAGONG', 'THESSALONIKI', 'BUENOS AIRES', 'MOJI', 'VALENCIA', 'TIHI',
    'KAMALAPUR/DHAKA', 'SAVANNAH', 'OSAKA', 'AHMEDABAD', 'PORT SAID WEST', 'NIIGATA', 'BUSAN',
    'SANTOS', 'BANGALORE', 'CEBU', 'SAVANNAH GEORGIA', 'CORK PORT, IRELAND', 'YOKOHAMA', 'KOBE',
    'NAGOYA', 'MUNDRA', 'ISTANBUL', 'JAKARTA', 'BELAWAN', 'HAIPHONG', 'MERSIN', 'AMBARLI',
    'INCHEON', 'COLOMBO', 'CHENNAI', 'JEBEL ALI', 'SURABAYA', 'BANGKOK', 'LAEM CHABANG', 'CAT LAI',
    'DAMMAM', 'CHIBA', 'CHATTOGRAM', 'KAOHSIUNG', 'KLAIPEDA', 'VENICE', 'SALERNO', 'RAVENNA',
    'LA SPEZIA', 'CONSTANTA', 'FREMANTLE', 'VANCOUVER', 'TORONTO (HALIFAX)', 'TORONTO (VANCOUVER)',
    'MONTREAL (HALIFAX)', 'MONTREAL (VANCOUVER)', 'MONTREAL (ALL WATER SERVICE)', 'WINNIPEG',
    'BALTIMORE', 'PYEONGTAEK', 'LONG BEACH', 'IZMIT', 'KUMPORT', 'ALEXANDRIA', 'BRISBANE',
    'MELBOURNE', 'AUCKLAND', 'TAURANGA', 'LOS ANGELES', 'PHILADELPHIA', 'MONTEVIDEO',
    'TANJUNG PRIOK (JAKARTA)', 'MANZANILLO', 'MALAGA', 'KOLKATA', 'GEBZE', 'DILIKELESI',
    'BILBAO', 'BUENAVENTURA', 'HAMAD', 'CAMDEN', 'COPENHAGEN', 'CHICAGO', 'MILWAUKEE',
    'PARANAGUA', 'ALTAMIRA', 'LOME', 'BUDAPEST', 'HELSINKI', 'TOKYO', 'DOHA', 'NAVEGANTES',
    'ITAPOA', 'FUNABASHI', 'ROSARIO', 'BOURGES', 'SIHANOUKVILLE', 'DILISKELESI', 'PIPAVAV',
    'KATTUPALLI', 'VISAKHAPATNAM', 'HALDIA', 'DHAKA & KAMLAPUR', 'JEDDAH', 'AL-SOKHNA',
    'AQABA', 'DJIBOUTI', 'DAMIETTA', 'IZMIR', 'LAT KRABANG', 'MANILA', 'NHAVA SHEVA',
    'BOSTON', 'CHARLESTON', 'NORFOLK', 'JACKSONVILLE', 'OAKLAND', 'MIAMI (ALL WATER)',
    'EDMONTON (VANCOUVER)', 'SAKASTOON', 'YANGON'
]

async def main():
    parser = argparse.ArgumentParser(description='Quick Sourcing Batch Benchmark Runner')
    parser.add_argument('--origin', default='Pasir Gudang, Malaysia', help='Origin port name/locode')
    parser.add_argument('--carriers', nargs='+', default=['GREENX', 'HAPAG_LLOYD', 'CMA_CGM', 'ONE', 'MAERSK'], help='Carriers to search')
    parser.add_argument('--limit', type=int, default=168, help='Number of destination ports to search')
    parser.add_argument('--output', default='Pasir_Gudang_168_Tariff_Rates.xlsx', help='Output Excel file path')
    args = parser.parse_args()

    destinations = DEFAULT_140_PORTS[:args.limit]
    print('================================================================')
    print(' [QUICK SOURCING BATCH BENCHMARK RUNNER]')
    print(f' Origin: {args.origin}')
    print(f' Total Destinations: {len(destinations)}')
    print(f' Target Carriers: {args.carriers}')
    print(' Search Mode: QUICK (1 cheapest quote card within 14-day window)')
    print(f' Output File: {args.output}')
    print('================================================================\n')
    print('[READY] Standalone Quick Sourcing batch runner script initialized successfully.')

if __name__ == '__main__':
    asyncio.run(main())
