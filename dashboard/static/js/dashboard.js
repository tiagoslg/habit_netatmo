class Dashboard {
    constructor(deviceId, moduleId, typeMeasure, stationOrModule, lastCheck) {
        this.deviceId = deviceId;
        this.moduleId = moduleId;
        this.typeMeasure = typeMeasure;
        this.stationOrModule = stationOrModule;
        this.lastDataTime = lastCheck;
        this.data = ''
    }

    setLastCheck(value){
        document.getElementById(`${this.deviceId}-last-check`).innerHTML = value
    }

    setData(valueList){
        let listReturn = '';
        for (var i = 0; i < valueList.length; i++) {
            listReturn += `<li>${valueList[i][0]}: ${valueList[i][1]}</li>`;
        }
        document.getElementById(`${this.deviceId}-data`).innerHTML = `<ul>${listReturn}</ul>`
    }

    setDataTime(value){
        document.getElementById(`${this.deviceId}-data-time`).innerHTML = value
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
        $.when(this.getData()).done( () =>
        {
            let data = this.data;
            if (data.status === 200 && data.data.found) {
                this.setLastCheck(data.time_server);
                this.setData(data.data.results);
                this.lastDataTime = data.data.beg_time;
                this.setDataTime(this.lastDataTime);
            }
            return data
        })
    }
}