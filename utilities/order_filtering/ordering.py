import pandas as pd


class Ordering:
    def order_filtering(
        response_data,
        params,
        params_direction,
        sort_by_list,
        combine_list,
        combine=False,
    ):
        sort_by = []
        order_by_direction = []
        if params:
            sort_by = [
                param.strip()
                for param in params.split(",")
                if param.strip() in sort_by_list
            ]
            if sort_by:
                order_by_direction = [
                    True if params_direction.strip() == "ASC" else False
                    for params_direction in params_direction.split(",")
                ]
            if len(order_by_direction) < len(sort_by):
                order_by_direction = order_by_direction + [True] * (
                    len(sort_by) - len(order_by_direction)
                )
        if sort_by is None:
            sort_by += ["created_at"]
            order_by_direction += [False]

        if sort_by:
            try:
                df = pd.DataFrame(response_data).fillna("")
                if combine:
                    if combine_list[0] not in df.columns:
                        df[combine_list[0]] = ""
                    if combine_list[1] not in df.columns:
                        df[combine_list[1]] = ""
                    df["name"] = df[combine_list[0]].astype(str) + df[
                        combine_list[1]
                    ].astype(str)
                df.sort_values(by=sort_by, ascending=order_by_direction, inplace=True)
                if combine:
                    df.drop(columns=["name"], inplace=True)
                response_data = df.fillna("").to_dict(orient="records")

            except Exception:
                return response_data
        return response_data
