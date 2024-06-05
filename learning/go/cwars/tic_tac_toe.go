package main

func IsSolved(board [3][3]int) int {

	var idxs = []int{0, 1, 2}
	var ps = []int{1, 2}
	for _, p := range ps {
		for _, i := range idxs {
			if is_row_won_by_p(board, i, p) ||
			   is_col_won_by_p(board, i, p) {
				return p
			}
		}

		if (board[0][0] == p) && (board[1][1] == p) && (board[2][2] == p) ||
		   (board[2][0] == p) && (board[1][1] == p) && (board[0][2] == p)  {
			return p
		}
	}

	if any_0(board) {
		return -1
	}

	return 0
}

func is_row_won_by_p(board [3][3]int, i, p int) bool {
	return (board[i][0] == p) && (board[i][1] == p) && (board[i][2] == p)
}

func is_col_won_by_p(board [3][3]int, i, p int) bool {
	return (board[0][i] == p) && (board[1][i] == p) && (board[2][i] == p)
}

func any_0(board [3][3]int) bool {
	for _, row := range board {
		for _, v := range row {
			if v == 0 {
				return true
			}
		}
	}
	return false
}