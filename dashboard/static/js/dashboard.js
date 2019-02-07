class RefreshAccessToken {
    constructor() {
        this._elCSRFToken = $('[name=csrfmiddlewaretoken]');
    }

    get csrfToken(){
        return this._elCSRFToken.val()
    }

    async refreshAccessToken(){
        await $.ajax({
            type: 'POST',
            url: 'refresh_access_token/',
            data: {},
            success: (result)=>{
                localStorage.setItem("access_token", result.access_token);
                localStorage.setItem("expires_in", parseInt(result.token_expires));
            },
            beforeSend: (xhr, settings)=>{
                xhr.setRequestHeader("X-CSRFToken", this.csrfToken);
            },
            dataType: 'json'
        });
        return true;
    }
}

class Dashboard {
    constructor(deviceId, moduleId, typeMeasure, stationOrModule, lastCheck) {
        this.deviceId = deviceId;
        this.moduleId = moduleId;
        this.typeMeasure = typeMeasure;
        this.stationOrModule = stationOrModule;
        this.lastDataTime = lastCheck;
        this.data = '';
        this.onDocumentReady();
    }

    static timeConverter(UNIX_timestamp){
        let a = new Date(UNIX_timestamp * 1000);
        let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        let year = a.getFullYear();
        let month = months[a.getMonth()];
        let date = "0" + a.getDate();
        let hour = "0" + a.getHours();
        let min = "0" + a.getMinutes();
        let sec = "0" + a.getSeconds();
        let time = date.substr(-2) + ' ' + month + ' ' + year + ' ' + hour.substr(-2) + ':' + min.substr(-2) + ':' + sec.substr(-2) ;
        return time;
    }

    getElementId(){
        let elementId = this.deviceId;
        if (this.stationOrModule === 'module'){elementId = this.moduleId}
        return elementId
    }

    setLastCheck(value){
        document.getElementById(`${this.getElementId()}-last-check`).innerHTML = value
    }

    setData(valueList){
        let listReturn = '';
        for (var i = 0; i < valueList.length; i++) {
            listReturn += `<li>${valueList[i][0]}: ${valueList[i][1]}</li>`;
        }
        document.getElementById(`${this.getElementId()}-data`).innerHTML = `<ul>${listReturn}</ul>`
    }

    setDataTime(value){
        document.getElementById(`${this.getElementId()}-data-time`).innerHTML = value
    }

    getUrl(){
        if (this.stationOrModule === 'station'){
            return `get_station/${this.deviceId}/`
        }
        return `get_temperature/${this.deviceId}/`
    }

    async getData(){
        let data = {
            'access_token': localStorage.getItem("access_token"),
            'module_id': this.moduleId,
            'type_measure': this.typeMeasure,
            'start_date': parseInt(this.lastDataTime - 3600),
        };

        await $.ajax({
            type: 'GET',
            url: this.getUrl(),
            data: data,
            success: (result)=>{
                this.data = result;
            },
            dataType: 'json'
        });
    }

    updateTable(){
        if(localStorage.getItem('expires_in') <= (Math.floor(Date.now() / 1000) + 15)){
            $.when(RefreshAccessToken.refreshAccessToken()).done( () => {
                this.updateTable();
            });
        } else {
            $.when(this.getData()).done( () =>
            {
                let data = this.data;
                if (data.status === 200 && data.data.found) {
                    this.setLastCheck(Dashboard.timeConverter(data.time_server));
                    this.setData(data.data.results);
                    this.lastDataTime = data.data.beg_time;
                    this.setDataTime(Dashboard.timeConverter(this.lastDataTime));
                }
                return data
            })
        }
    }

    onDocumentReady(){
	    $(document).ready(()=>{
	        this.updateTable();
	        setInterval(() => { this.updateTable(); }, 600000);
        });
    }
}

class GetLogStatus{
    constructor(deviceId) {
        this.data = '';
        this.deviceId = deviceId;
        this.onDocumentReady();
    }

    setLastCheck(value){
        document.getElementById(`${this.deviceId}-last-check`).innerHTML = value;
    }

    setData(value){
        document.getElementById(`${this.deviceId}-data`).innerHTML = value;
    }

    setDataTime(value){
        document.getElementById(`${this.deviceId}-data-time`).innerHTML = value;
    }

    async getData(){
        await $.ajax({
            type: 'GET',
            url: `/get_camera_con_status/${this.deviceId}/`,
            data: {},
            success: (result)=>{
                this.data = result;
            },
            dataType: 'json'
        });
    }

    updateTable(){
        if(localStorage.getItem('expires_in') <= (Math.floor(Date.now() / 1000) + 15)){
            $.when(RefreshAccessToken.refreshAccessToken()).done( () => {
                this.updateTable();
            });
        } else {
            $.when(this.getData()).done( () =>
            {
                let data = this.data;
                if (data.status === 200) {
                    this.setLastCheck(Dashboard.timeConverter(data.time_server));
                    this.setData(data.message);
                    this.lastDataTime = data.time_event;
                    this.setDataTime(Dashboard.timeConverter(this.lastDataTime));
                }
                return data
            })
        }
    }

    onDocumentReady(){
	    $(document).ready(()=>{
	        this.updateTable();
	        setInterval(() => { this.updateTable(); }, 60000);
        });
    }
}