StatisticApp = function () {

    var self = this;

    //this.ct;
    //this.id;
    this.resource_uri;
    this.dom_id = 'statistics_container';
    this.loaded = false;
    this.loading = false;


    this.init = function () {
        console.log('StatisticApp: init', self.resource_uri);
    };


    this.show = function () {
        console.log('StatisticApp: load - loaded:', self.loaded);


        if (!self.loaded) {
            self.load();
        }

    };

    this.load = function () {

        var url = self.resource_uri + 'stats/';


        $.get(url, function (data) {
            console.log('response data:', data);

            $.plot('#' + self.dom_id, data, {
                xaxis: {
                    mode: "time",
                    minTickSize: [1, "month"]
                },
                grid: {
                    show: true,
                    aboveData: true,
                    color: '#999999',
                    backgroundColor: '#ffffff',
                    margin: 0,
                    borderWidth: 0,
                    borderColor: null,
                    clickable: true,
                    hoverable: true,
                    autoHighlight: true

                },
                legend: {

                },
                series: {
                    lines: { show: true, fill: false},
                    points: { show: false, fill: false }
                },
                colors: ["#47248F", "#00BB00", "#00ffff"],
                crosshair: {
                    mode: "x"
                }
            })


            /*
             var line1 = [
             ['2013/12/01', 1566],
             ['2014/01/01', 278],
             ['2014/02/01', 978],
             ['2014/03/01', 278],
             ['2014/04/01', 578],
             ['2014/05/01', 566],
             ['2014/06/01', 1566],
             ['2014/07/01', 1566],
             ['2014/08/01', 1566],
             ['2014/09/01', 1566],
             ['2014/10/01', 1566],
             ['2014/11/01', 1566]
             ];


             var plot1 = $.jqplot(self.dom_id, [line1], {
             title: 'Data Point Highlighting',
             axes: {
             xaxis: {
             renderer: $.jqplot.DateAxisRenderer,
             numberTicks: 2,
             syncTicks: true,
             autoscale: false,
             tickOptions: {
             formatString: '%Y %b'
             }
             },
             yaxis: {
             tickOptions: {
             formatString: '%i'
             }
             }
             },
             //highlighter: {
             //    show: true,
             //    sizeAdjust: 7.5
             //},
             cursor: {
             show: false
             }
             });
             */


            $('.message', $('#' + self.dom_id)).hide();


        });

        /*
         setTimeout(function () {
         $('#' + self.dom_id).html('<h1>stats</h1>');
         self.loaded = true;
         }, 2000);
         */

    };


};