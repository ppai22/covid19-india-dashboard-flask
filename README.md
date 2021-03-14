# Covid19 India Dashboard
Simple dashboard with Covid19 data available for India built using Flask

This is a work in progress and has been deployed [here](https://covid-19-india-dashboard-flask.herokuapp.com/) in the initial version.

### Features currently enabled:

- India map in home page with total active cases
- Clicking on the state names opens the state page
- State page shows confirmed cases, recovered cases, deceased cases count along with cumulative curve, recovery rate
- Vaccination data shown in the Vaccination page (at India level) (Data from [Our World in Data](https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/country_data/India.csv))

### Tools used:
- [Flask](https://flask.palletsprojects.com/en/1.1.x/) framework
- [Chart JS](https://www.chartjs.org/) for the bar and line charts
- [HighCharts](https://www.highcharts.com/) for the India map
- [Bootstrap](https://getbootstrap.com/) for frontend

- Special mention to the [covid19india.org](https://www.covid19india.org/) team for the open source [APIs](https://api.covid19india.org/) with the data
