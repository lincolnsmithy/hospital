from shiny import App, ui, render
import pandas as pd
import matplotlib.pyplot as plt

# Read the data
df = pd.read_csv("data/Hospital_and_Other_data_Q2_2025.csv")

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Filters"),
        ui.input_select(
            "state",
            "Select State",
            choices=["All"] + sorted(df["STATE_CD"].unique().tolist())
        ),
        ui.input_select(
            "provider_type",
            "Provider Type",
            choices=["All"] + sorted(df["PRVDR_CTGRY_CD"].unique().tolist())
        )
    ),
    ui.navset_tab(
        ui.nav_panel("Overview",
                     ui.layout_column_wrap(
                         ui.value_box(
                             "Total Facilities",
                             ui.output_text("total_facilities"),
                             showcase=ui.HTML('<i class="fa fa-hospital"></i>')
                         ),
                         ui.value_box(
                             "States Coverage",
                             ui.output_text("states_count"),
                             showcase=ui.HTML('<i class="fa fa-map"></i>')
                         ),
                         ui.value_box(
                             "Provider Types",
                             ui.output_text("provider_types"),
                             showcase=ui.HTML('<i class="fa fa-user-md"></i>')
                         ),
                         width=1 / 3
                     ),
                     ui.card(
                         ui.card_header("Facilities by State"),
                         ui.output_plot("state_distribution")
                     ),
                     ui.layout_column_wrap(
                         ui.card(
                             ui.card_header("Provider Type Distribution"),
                             ui.output_plot("provider_distribution")
                         ),
                         ui.card(
                             ui.card_header("Facility Details"),
                             ui.output_table("facility_table")
                         ),
                         width=1 / 2
                     )
                     ),
        ui.nav_panel("Detailed Analysis",
                     ui.card(
                         ui.card_header("Detailed Facility Information"),
                         ui.output_data_frame("detailed_table")
                     )
                     )
    )
)


def server(input, output, session):
    def get_filtered_data():
        """Helper function to filter data based on inputs"""
        filtered_df = df.copy()

        if input.state() != "All":
            filtered_df = filtered_df[filtered_df["STATE_CD"] == input.state()]

        if input.provider_type() != "All":
            filtered_df = filtered_df[filtered_df["PRVDR_CTGRY_CD"] == int(input.provider_type())]

        return filtered_df

    @render.text
    def total_facilities():
        filtered_df = get_filtered_data()
        return str(len(filtered_df))

    @render.text
    def states_count():
        return str(df["STATE_CD"].nunique())

    @render.text
    def provider_types():
        return str(df["PRVDR_CTGRY_CD"].nunique())

    @render.plot
    def state_distribution():
        filtered_df = get_filtered_data()
        state_counts = filtered_df["STATE_CD"].value_counts()

        fig, ax = plt.subplots(figsize=(12, 6))
        state_counts.plot(kind='bar', ax=ax)
        ax.set_title("Facilities by State")
        ax.set_xlabel("State")
        ax.set_ylabel("Count")
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        return fig

    @render.plot
    def provider_distribution():
        filtered_df = get_filtered_data()
        provider_counts = filtered_df["PRVDR_CTGRY_CD"].value_counts()

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(provider_counts.values, labels=provider_counts.index, autopct='%1.1f%%')
        ax.set_title("Provider Type Distribution")
        return fig

    @render.table
    def facility_table():
        filtered_df = get_filtered_data()
        # Display available columns - adjust based on your actual CSV structure
        display_columns = []

        # Check which columns exist in the dataframe
        if "PRVDR_NM" in filtered_df.columns:
            display_columns.append("PRVDR_NM")
        if "STATE_CD" in filtered_df.columns:
            display_columns.append("STATE_CD")
        if "PRVDR_CTGRY_CD" in filtered_df.columns:
            display_columns.append("PRVDR_CTGRY_CD")

        # If no specific columns found, use first few columns
        if not display_columns:
            display_columns = filtered_df.columns[:3].tolist()

        return filtered_df.head(10)[display_columns]

    @render.data_frame
    def detailed_table():
        filtered_df = get_filtered_data()
        return filtered_df.head(100)


app = App(app_ui, server)