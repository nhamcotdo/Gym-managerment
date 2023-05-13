/**
 * Dashboard Analytics
 */

let cardColor, headingColor, axisColor, shadeColor, borderColor;

cardColor = config.colors.white;
headingColor = config.colors.headingColor;
axisColor = config.colors.axisColor;
borderColor = config.colors.borderColor;
const GetData = async function (year) {
  let data = {};
  await fetch(`${urls.get_revenue}?year=${year}`)
    .then((response) => response.json())
    .then((res) => {
      data = res;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  return data;
};
const IncomeChart = function (data) {
  const revenueChartEl = document.querySelector("#revenueChart"),
    revenueChartConfig = {
      series: [
        {
          data: data,
        },
      ],
      chart: {
        height: 215,
        parentHeightOffset: 0,
        parentWidthOffset: 0,
        toolbar: {
          show: false,
        },
        type: "area",
      },
      dataLabels: {
        enabled: false,
      },
      stroke: {
        width: 2,
        curve: "smooth",
      },
      legend: {
        show: false,
      },
      markers: {
        size: 6,
        colors: "transparent",
        strokeColors: "transparent",
        strokeWidth: 4,
        discrete: [
          {
            fillColor: config.colors.white,
            seriesIndex: 0,
            dataPointIndex: 7,
            strokeColor: config.colors.primary,
            strokeWidth: 2,
            size: data.length,
            radius: 8,
          },
        ],
        hover: {
          size: 7,
        },
      },
      colors: [config.colors.primary],
      fill: {
        type: "gradient",
        gradient: {
          shade: shadeColor,
          shadeIntensity: 0.6,
          opacityFrom: 0.5,
          opacityTo: 0.25,
          stops: [0, 95, 100],
        },
      },
      grid: {
        borderColor: borderColor,
        strokeDashArray: 3,
        padding: {
          top: -20,
          bottom: -8,
          left: -10,
          right: 8,
        },
      },
      xaxis: {
        categories: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        axisBorder: {
          show: false,
        },
        axisTicks: {
          show: false,
        },
        labels: {
          show: true,
          style: {
            fontSize: "13px",
            colors: axisColor,
          },
        },
      },
      yaxis: {
        labels: {
          show: false,
        },
        min: Math.min(...data),
        max: Math.max(...data),
        tickAmount: 4,
      },
    };
  if (typeof revenueChartEl !== undefined && revenueChartEl !== null) {
    const revenueChart = new ApexCharts(revenueChartEl, revenueChartConfig);
    revenueChart.render();
  }
};

const GrowthChartEl = function (data) {
  const growthChartEl = document.querySelector("#growthChart"),
    growthChartOptions = {
      series: [data],
      labels: ["Tăng trưởng"],
      chart: {
        height: 240,
        type: "radialBar",
      },
      plotOptions: {
        radialBar: {
          size: 150,
          offsetY: 10,
          startAngle: -150,
          endAngle: 150,
          hollow: {
            size: "55%",
          },
          track: {
            background: cardColor,
            strokeWidth: "100%",
          },
          dataLabels: {
            name: {
              offsetY: 15,
              color: headingColor,
              fontSize: "15px",
              fontWeight: "600",
              fontFamily: "Public Sans",
            },
            value: {
              offsetY: -25,
              color: headingColor,
              fontSize: "22px",
              fontWeight: "500",
              fontFamily: "Public Sans",
            },
          },
        },
      },
      colors: ["red"],
      fill: {
        type: "gradient",
        gradient: {
          shade: "dark",
          shadeIntensity: 0.5,
          gradientToColors: ["#71dd37"],
          inverseColors: true,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [30, 70, 100],
        },
      },
      stroke: {
        dashArray: 5,
      },
      grid: {
        padding: {
          top: -35,
          bottom: -10,
        },
      },
      states: {
        hover: {
          filter: {
            type: "none",
          },
        },
        active: {
          filter: {
            type: "none",
          },
        },
      },
    };
  if (typeof growthChartEl !== undefined && growthChartEl !== null) {
    const growthChart = new ApexCharts(growthChartEl, growthChartOptions);
    growthChart.render();
  }
};
const Reload = async function (selectYear) {
  const dropdownButton = document.getElementById("growthReportId");
  dropdownButton.textContent = selectYear;
  let data = await GetData(selectYear);
  if (data) {
    IncomeChart(Object.values(data.amounts_by_month));
    GrowthChartEl(
      parseInt((data.total_amount / data.total_amount_lastyear) * 100).toFixed(
        2
      )
    );

    $("#lastMonth").text(data.last_month_amount.toLocaleString());
    $("#curMonth").text(data.current_month_amount.toLocaleString());
    $("#amount").text(data.total_amount.toLocaleString());
    $("#amountLastyear").text(data.total_amount_lastyear.toLocaleString());
    $("#amount_select").text(data.total_amount_select.toLocaleString());
    $("#curYear").text(new Date().getUTCFullYear());
    $("#lastYear").text(new Date().getUTCFullYear() - 1);

    let percentageIncrease =
      ((data.current_month_amount - data.last_month_amount) /
        data.last_month_amount) *
      100;
    const smallElement = document.querySelector("#percentageIncrease");
    const title = document.querySelector("#_percentageIncrease");
    const congratulation = document.querySelector("#Congratulation");

    if (percentageIncrease > 0) {
      smallElement.innerHTML = `<i class="bx bx-up-arrow-alt"></i> +${percentageIncrease.toFixed(
        2
      )}%`;
      smallElement.classList.remove("text-danger");
      smallElement.classList.add("text-success");

      title.textContent = `tăng ${percentageIncrease.toFixed(2)} %`;
      title.classList.remove("text-danger");
      title.classList.add("text-success");
      congratulation.textContent = "Chúc mừng 🎉";
    } else if (percentageIncrease < 0) {
      const negativePercentageIncrease =
        Math.abs(percentageIncrease).toFixed(2);
      smallElement.innerHTML = `<i class="bx bx-down-arrow-alt"></i> -${negativePercentageIncrease}%`;
      smallElement.classList.add("text-danger");
      smallElement.classList.remove("text-success");
      title.textContent = `giảm ${percentageIncrease.toFixed(2)} %`;
      title.classList.add("text-danger");
      title.classList.remove("text-success");
      congratulation.textContent = "Rất tiếc 🥹";
    } else {
      smallElement.innerHTML = `${percentageIncrease.toFixed(2)}%`;
    }
  }
};
$("document").ready(function () {
  // Year
  fetch(urls.get_years)
    .then((response) => response.json())
    .then(async (res) => {
      const listYears = res.list_years;
      const currentYear = res.current_year;

      const dropdownYears = document.getElementById("dropdownYears");
      listYears.forEach((year) => {
        const link = document.createElement("a");
        link.classList.add("dropdown-item");
        link.href = `javascript:Reload(${year})`;
        link.textContent = year;
        dropdownYears.appendChild(link);
      });

      const dropdownButton = document.getElementById("growthReportId");
      dropdownButton.textContent = currentYear;
      await Reload(currentYear);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});
