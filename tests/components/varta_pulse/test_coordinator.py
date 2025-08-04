"""Tests for Varta Pulse Coordinator."""

import pytest

from homeassistant.components.varta_pulse.coordinator import VartaPulseCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


class DummySession:
    """Dummy HTTP session for coordinator tests."""

    async def get(self, url: str):
        """Simulate aiohttp.ClientSession.get for test endpoints."""

        class DummyResp:
            def __init__(self, text: str, status: int = 200) -> None:
                self._text = text
                self.status = status

            async def text(self) -> str:
                return self._text

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        # Return example data for each endpoint
        if url.endswith("/cgi/info.js"):
            return DummyResp(
                """
Device_Type = "M-UF.273-00A";
Device_Serial = "0123456789";
Device_Description = "VARTA";
EMS_Serial = "K001234";
SW_ID_EMS = 0xae;
HW_ID_EMS = 0x03;
SW_Version_EMS = "C21010705";
IP = "192.168.2.12";
Netmask = "255.255.255.0";
Gateway = "192.168.2.1";
DNS = "192.168.2.1";
Anz_Charger = 1;
Soll_Charger = 1;
Serial_WR = "K005678";
MAC_WR = " 5B68E8";
SW_ID_WR = 0xac;
HW_ID_WR = 0x00;
SW_Version_WR = "C11010503";
BL_Version_WR = "1.3.0.5";
Serial_EMeter = "M487654";
MAC_EMeter = " 0CC200";
SW_Version_EMeter = "C41000400";
BL_Version_EMeter = "x.1.0.6";
HW_ID_EMeter = 0x21;
IndexMinVersion = 15;
IndexMaxVersion = 15;
Charger_Serial = [ "K005678"];
Charger_MAC = [ " EA559C"];
SW_ID_Charger = [ 0xA0];
AppHW_ID_Charger = [ 0x12];
HW_ID_Charger = [ 0x04];
SW_Version_Charger = [ "C31010609"];
BL_Version_Charger = [ "3.0.4"];
Battery_Serial = "EM048126P3S7BMA2006298096";
BMS_Serial = "2006110381";
BMS_SW = "1.0";
BMS_HW = "0.2";
BatteryHW = ["0.2"];
BMS_Type = "7";
P_EMS_Max = 2500;
CountryID = 0;
norm_ext = 0;
gridcode = 65535;
BM_Update = ["03.04.2025 13:11:31"];
BM_UpdateSW = ["1.0.0.20"];
BM_Production = ["2006298096"];
LG_Battery_Serial = ["EM048126P3S7xxx2006298096"];
"""
            )
        if url.endswith("/cgi/param"):
            return DummyResp(
                """
IP= "0.0.0.0";
NETMASK= "255.255.255.0";
DNS= "0.0.0.0";
GATEWAY= "0.0.0.0";
DHCP= 1;
VPN_SERV= "vpn-pu.varta-storage-portal.com";
VPN_EN= 1;
TIME_SERV= "vpn.varta-storage-portal.com";
DATE= "03.08.2025";
TIME= "22:56:33";
TIME_SHIFT_1= "06.10";
TIME_SHIFT_2= "07.04";
DESCR= "VARTA";
TIME_ZONE= "1";
ADJ_DLS= 1;
LED_SPEED0= 60;
LED_SPEED1= 10;
LED_PAUSE= 10;
LED_MODE= 0;
FTP_EN= 1;
FTP_SERV= "ftp-pu.varta-storage-portal.com";
FTP_PAUSE= 10;
REBOOT_DAY= 64;
REBOOT_HOUR= 3;
VSCHECK_EN= 1;
VSWATCH_EN= 1;
CURRSENSCFG= 15;
T_FILTER= 6000;
SCHIEF_SMAX= 4600;
COUPLING= 0;
EZ_SERIAL= 4294967295;
KASKADE_ID= 4294967295;
QFKT= 0;
QTIME= 10;
QPMIN= 8;
QCOSMAN= 0;
QMAN= 0;
QPX1= 46;
QPY1= 0;
QPX2= 92;
QPY2= 100;
QPX3= 0;
QPY3= 0;
QPX4= 0;
QPY4= 0;
QP_USTART = 241;
QP_USTOP = 230;
QUX1= 218;
QUY1= -50;
QUX2= 225;
QUY2= 0;
QUX3= 239;
QUY3= 0;
QUX4= 246;
QUY4= 50;
QUKF= 1;
QU_PSTART = 0;
QU_PSTOP = 0;
QU_DELAY = 0;
PUFKT = 0;
PUKNICK = 253;
PUGRENZ = 258;
PUTIME = 0;
PSP= 101;
PSP_TIME = 0;
UNETZ_OK_O= 1000;
UNETZ_OK_U= 1000;
UNETZ_ERR_DELAY= 0;
UNETZ_MIN_1ST= 196;
UNETZ_MAX_1ST= 253;
FNETZ_MIN_1ST= 4750;
FNETZ_MAX_1ST= 5005;
UNETZ_MIN_START= 196;
UNETZ_MAX_START= 253;
FNETZ_MIN_START= 4750;
FNETZ_MAX_START= 5010;
UNETZ_MIN_BETR= 184;
UNETZ_MIN_BETR2= 104;
UNETZ_MAX_BETR= 288;
UNETZ_MAX_BETR2= 264;
UNETZ_MAX10= 253;
FNETZ_MIN_BETR= 4750;
FNETZ_MIN_BETR2= 4750;
FNETZ_MAX_BETR= 5150;
FNETZ_MAX_BETR2= 5150;
FNETZ_MIN_DEL1= 40;
FNETZ_MIN_DEL2= 40;
FNETZ_MAX_DEL1= 10;
FNETZ_MAX_DEL2= 10;
UNETZ_MIN_DEL1= 300;
UNETZ_MIN_DEL2= 30;
UNETZ_MAX_DEL1= 0;
UNETZ_MAX_DEL2= 10;
TNETZ= 60;
TNETZERR= 60;
FREDP_O_S= 5;
FREDP_O_START= 5020;
FREDP_O_ENDE= 5150;
FREDP_O_OK= 5020;
FREDP_U_S= 2;
FREDP_U_START= 4980;
FREDP_U_ENDE= 4000;
FREDP_U_OK= 4980;
FREDP_STARTDELAY= 0;
FREDP_OKDELAY= 600;
T_IHOCHFREDP= 700;
T_IHOCHERR= 700;
T_IHOCHOK= 10;
SK_NAME= "TCRIP4";
SK_MAN= 0;
SK_EN= 0;
SK1_TAG= 0;
SK1_START= 0;
SK1_EIN_NOT= -1;
SK1_ENDE= 0;
SK1_EIN_SOC= 0;
SK1_EIN_SOC_TERM= 0;
SK1_EIN_FKT= 0;
SK1_EIN_FKT_WERT= 0;
SK1_EIN_FKT_TERM= 0;
SK1_AUS_SOC= 0;
SK1_AUS_SOC_TERM= 0;
SK1_AUS_SOC_AKT= 0;
SK1_AUS_P= 0;
SK1_AUS_P_TERM= 0;
SK1_AUS_P_AKT= 0;
SK1_AUS_ZEIT= 0;
SK1_AUS_ZEIT_AKT= 0;
SK1_DELAY= 60;
SK2_TAG= 0;
SK2_START= 0;
SK2_EIN_NOT= -1;
SK2_ENDE= 0;
SK2_EIN_SOC= 0;
SK2_EIN_SOC_TERM= 0;
SK2_EIN_FKT= 0;
SK2_EIN_FKT_WERT= 0;
SK2_EIN_FKT_TERM= 0;
SK2_AUS_SOC= 0;
SK2_AUS_SOC_TERM= 0;
SK2_AUS_SOC_AKT= 0;
SK2_AUS_P= 0;
SK2_AUS_P_TERM= 0;
SK2_AUS_P_AKT= 0;
SK2_AUS_ZEIT= 0;
SK2_AUS_ZEIT_AKT= 0;
SK2_DELAY= 60;
SK3_TAG= 0;
SK3_START= 0;
SK3_EIN_NOT= -1;
SK3_ENDE= 0;
SK3_EIN_SOC= 0;
SK3_EIN_SOC_TERM= 0;
SK3_EIN_FKT= 0;
SK3_EIN_FKT_WERT= 0;
SK3_EIN_FKT_TERM= 0;
SK3_AUS_SOC= 0;
SK3_AUS_SOC_TERM= 0;
SK3_AUS_SOC_AKT= 0;
SK3_AUS_P= 0;
SK3_AUS_P_TERM= 0;
SK3_AUS_P_AKT= 0;
SK3_AUS_ZEIT= 0;
SK3_AUS_ZEIT_AKT= 0;
SK3_DELAY= 60;
SK4_TAG= 0;
SK4_START= 0;
SK4_EIN_NOT= -1;
SK4_ENDE= 0;
SK4_EIN_SOC= 0;
SK4_EIN_SOC_TERM= 0;
SK4_EIN_FKT= 0;
SK4_EIN_FKT_WERT= 0;
SK4_EIN_FKT_TERM= 0;
SK4_AUS_SOC= 0;
SK4_AUS_SOC_TERM= 0;
SK4_AUS_SOC_AKT= 0;
SK4_AUS_P= 0;
SK4_AUS_P_TERM= 0;
SK4_AUS_P_AKT= 0;
SK4_AUS_ZEIT= 0;
SK4_AUS_ZEIT_AKT= 0;
SK4_DELAY= 60;
NORM_EXT= 0;
GRIDCODE= 65535;
BATT_SER= "EM01234567890123456789012";
DISFLAGS= 0;
KDL= 0;
SSC= 0;
CHRGLIMITER= 0;
CHRGLIMIT_TIME1= "00:00";
CHRGLIMIT_TIME2= "00:00";
CHRGLIMIT_SOC1= 3;
CHRGLIMIT_SOC2= 3;
CHRGLIMIT_VALUE= 20;
CHRGLIMIT_MONTH= 0;
ISSUNNYDAY= 0;
GRIDCHRG= 0;
GRIDCHRG_MONTH= 0;
GRIDCHRG_TIME1= "00:00";
GRIDCHRG_TIME2= "24:00";
GRIDCHRG_SOC= 100;
GRIDCHRG_PFACTOR= 100;
LOG_FIFA= 1;
"""
            )
        if url.endswith("/cgi/ems_conf.js"):
            return DummyResp(
                """
WR_Conf = ["EMS UG", "EMS OG", "EMS Timer", "PSoll", "U Verbund", "U WR", "I Wirk", "I Blind", "TempAmb", "TempHB", "TempEMS", "FNetz", "U N->PE", "OnlineStatus", "System State", "SK", "RB_IP", "RCMU", "IDrift", "UZwk", "Luefter Soll", "Luefter Ist", "WR Ctrl", "ENS Ctrl", "EMS Ctrl", "EMS Mode", "BetrFlags1", "BetrFlags2", "PMB", "EMB", "PAvailDCAC", "PAvailACDC", "MaxSchieflastACDC", "MaxSchieflastDCAC", "CountryID", "IO_Box", "SC OV_Val S1", "SC OV_Time S1", "SC UV_Val S1", "SC UV_Time S1", "SC OF_Val S1", "SC OF_Time S1", "SC UF_Val S1", "SC UF_Time S1", "SC OV_Val S2", "SC OV_Time S2", "SC UV_Val S2", "SC UV_Time S2", "SC OF_Val S2", "SC OF_Time S2", "SC UF_Val S2", "SC UF_Time S2", "General State"];
EMETER_Conf = ["U EMeter", "I EMeter L1", "I EMeter L2", "I EMeter L3", "F EMeter", "SensorState", "Iw PV L1", "Iw PV L2", "Iw PV L3", "Ib PV L1", "Ib PV L2", "Ib PV L3", "Is Verb L1", "Is Verb L2", "Is Verb L3", "Ib Verb L1", "Ib Verb L2", "Ib Verb L3"];
Charger_Conf = ["Index", "Enabled", "SOC_GS", "State", "U", "I", "UOut", "UVcc", "THT", "TTr", "TBoard", "PSoll", "SOHCmax", "SOHCuxtime", "SOHDmax", "SOHDuxtime", "ErrorFlags", "UNetz", "FNetz", "PAvailChrg", "PAvailDisc", "SOCMin", "SOCMax", "DABWinkel", "HelperFlags", "BetrFlags", "SteuerFlags", "BattState", "SVDFflags", "RSOCmin", "RSOCmax", "SOCcut", "DSOC_Thr1", "DSOC_Thr2", "SVDFtime", "SVDFcnt1s", "BattData"];
Batt_Conf = ["LG_Neo", "Type", "Alarms_Rack", "Warnings_Rack", "U_Rack", "I_Rack", "SOC_Rack", "SOH_Rack", "UMax_Rack", "IChrgLimit_Rack", "IDiscLimit_Rack", "Temp_Rack", "ModulData"];
Modul_Conf = ["Status", "Alarms_Modul", "Warnings_Modul", "Faults1_Modul", "Faults2_Modul", "IntErrors_Modul", "SOC_Modul", "SOH_Modul", "U_Modul", "I_Modul", "UMin_Modul", "UMax_Modul", "UAvg_Modul", "IChrgLimitBatt", "IDiscLimitBatt", "PChrgLimitBatt", "PDiscLimitBatt", "Temp1", "Temp2", "TempAvg", "BalTarg", "AnzCycles", "ModUserSOC", "SVDStat", "PackSerNr", "LifeEnergy", "RackSOCmax", "RackSOCmin", "SwVersFull", "CellVolt1", "CellVolt2", "CellVolt3", "CellVolt4", "CellVolt5", "CellVolt6", "CellVolt7", "CellVolt8", "CellVolt9", "CellVolt10", "CellVolt11", "CellVolt12", "CellVolt13", "CellVolt14"];
"""
            )
        if url.endswith("/cgi/ems_data.js"):
            return DummyResp(
                """
Zeit = "03.08.2025 22:56:34";
WR_Data = [-2500,2500,0,-294,2341,2340,-110,-34,30,35,24,5001,1111,1,3,0,"255.255.255.255",0,16,3840,47,50,100,30,100,1,17843779,285267200,0,0,2500,2500,2500,2500,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
EMETER_Data = [2342,55,-31,-29,5004,1,0,0,0,0,0,0,100,-220,-48,-84,-218,-39];
Charger_Data = [[0,1,72,104,5379,-546,3826,120,39,40,35,-294,0,0,0,0,0,2360,5001,2500,2500,0,100,-5070,18627616,32843,327,6931,21,71,95,75,20,5,1860,1860,
["LG_Neo",7,0,0,5370,-55,710,890,581,630,630,284,
  [ [24577,0,0,0,0,0,713,899,537,-55,3827,3848,3838,63,63,3385,3385,28,28,28,0,1028,719,0,2006298096,5784274,721,702,"1.0.0.20",3841,3838,3842,3843,3845,3848,3848,3841,3837,3827,3827,3831,3834,3828]  ]
]
]
];
"""
            )
        if url.endswith("/cgi/error.js"):
            return DummyResp(
                """
var ErrorList = [];
var NA_ErrorList = [[-1,0xffffffff],[-1,0xffffffff],[-1,0xffffffff],[-1,0xffffffff],[-1,0xffffffff]];
"""
            )
        return DummyResp("", status=404)


@pytest.mark.asyncio
async def test_async_update_data_types(
    hass: HomeAssistant, varta_config_entry: ConfigEntry
) -> None:
    """Test coordinator _async_update_data returns correct types."""
    coordinator = VartaPulseCoordinator(hass, varta_config_entry)
    # Patch session
    coordinator.session = DummySession()
    data = await coordinator._async_update_data()
    assert isinstance(data["param"].data, dict)
    assert isinstance(data["ems_data"].wr_data, dict)
    assert isinstance(data["ems_data"].emeter_data, dict)
    assert isinstance(data["ems_data"].charger_data, dict)
    assert isinstance(data["ems_data"].modules_data, list)
    assert isinstance(data["error"].error_list, list)
    assert isinstance(data["error"].na_error_list, list)
    assert "OnlineStatus" in data["ems_data"].wr_data
    assert "PSoll" in data["ems_data"].wr_data
    assert "I EMeter L3" in data["ems_data"].emeter_data
    assert "BattData" in data["ems_data"].charger_data
