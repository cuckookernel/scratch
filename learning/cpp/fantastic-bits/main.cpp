//
// Created by teo on 25/12/23.
//
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <limits>
#include <variant>
#include <algorithm>

// #include <algorithm>

using namespace std;

constexpr int UNDEF_INT = numeric_limits<int>::min();
constexpr float FIELD_MAX_X = 16000;
constexpr float FIELD_CTR_X = 8000;
constexpr float FIELD_MAX_Y = 7500;
constexpr float FIELD_CTR_Y = 3750;
constexpr float SNAFFLE_RADIUS = 150;
constexpr float WIZARD_RADIUS = 400;
constexpr float MAX_WIZ_THRUST = 150;  // max thrust for move
constexpr float MAX_THROW_POW = 500;  // max power for throw
constexpr float FORCE_TO_DELTA_VEL = 1.0; // ???
constexpr float VEL_TO_DELTA_POS = 1.0; // ???


/**
 * Grab Snaffles and try to throw them through the opponent's goal!
 * Move towards a Snaffle and use your team id to determine where you need to throw it.
 **/

enum class EntityT {
    WIZ,
    OPP,
    SNF,
    BLG,
    UNDEF
};

class GameException : public exception {
private:
    const string msg;

public:
    explicit GameException(string&& msg_) : msg(msg_) {};

    const char* what() {
        return msg.c_str();
    };

};

EntityT from_str(const string& type_str) {
    if (type_str == "WIZARD") {
        return EntityT::WIZ;
    } else if (type_str == "OPPONENT_WIZARD") {
        return EntityT::OPP;
    } else if (type_str == "SNAFFLE") {
        return EntityT::SNF;
    } else if (type_str == "BLUDGER") {
        return EntityT::BLG;
    } else {
        throw GameException(string("unknown entity type") + string(type_str));
    }
}

auto clip(int x, int l, int u) -> int { return max(l, min(x, u));}
auto clip(float x, float l, float u) -> float { return max(l, min(x, u)); }

typedef mt19937 Rng;

struct Vec2D;

struct Point2D {
    float x;
    float y;

    constexpr Point2D(float x_, float y_) : x(x_), y(y_) {}

    [[nodiscard]]
    auto distance_to(const Point2D &other) const -> float {
        auto dx = x - other.x;
        auto dy = y - other.y;
        return sqrt(dx * dx + dy * dy);
    }

    auto operator+=(const Vec2D& rhs) -> Point2D&;
};

struct Vec2D {
    float dx;
    float dy;

    Vec2D(float dx, float dy): dx(dx), dy(dy) {}

    [[nodiscard]]
    auto operator+(const Vec2D& other) const -> Vec2D { return Vec2D {dx + other.dx, dy + other.dy};}
    [[nodiscard]]
    auto operator-(const Vec2D& other) const -> Vec2D { return Vec2D {dx - other.dx, dy - other.dy};}
    [[nodiscard]] auto l2() const -> float { return sqrt(dx * dx + dy * dy);}
    [[nodiscard]] auto l2_sq() const -> float { return dx * dx + dy * dy;}
    [[nodiscard]] auto dot(const Vec2D& other) const -> float { return (dx * other.dx + dy * other.dy); }
    [[nodiscard]] auto unit() const -> Vec2D { const auto norm = l2();
        return Vec2D{dx / norm, dy / norm};
    }
    [[nodiscard]] auto operator*(float scalar) const -> Vec2D { return Vec2D{dx * scalar, dy * scalar}; }

    [[nodiscard]]
    auto project(const Vec2D& w) const -> Vec2D {
        // projection of this vector in direction of other
        // z = (v . w) w / ||w||^2
        const auto& v = *this;
        const auto factor = v.dot(w) / w.l2_sq();
        return w * factor;
    }

    auto operator+=(const Vec2D& rhs) -> Vec2D& { dx += rhs.dx; dy += rhs.dy; return *this;}
};

auto operator+(const Point2D& p, const Vec2D& d) -> Point2D {
    return Point2D{p.x + d.dx, p.y + d.dy};
}

auto operator-(const Point2D& p, const Vec2D& d) -> Point2D {
    return Point2D {p.x - d.dx, p.y - d.dy};
}

auto operator-(const Point2D& p1, const Point2D& p2) -> Vec2D {
    return Vec2D {p1.x - p2.x, p1.y - p2.y};
}

auto operator*(float a, const Vec2D& v) -> Vec2D {
    return Vec2D {a * v.dx , a * v.dy};
}

auto Point2D::operator+=(const Vec2D& rhs) -> Point2D& { x += rhs.dx; y += rhs.dy; return *this;}

constexpr Point2D GOAL_0 = Point2D  {16000, 3750};
constexpr Point2D GOAL_1 = Point2D  {0, 3750};


struct Entity {
    int entity_id; // entity identifier
    EntityT entity_type = EntityT::UNDEF; // "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)

    Point2D pos;
    Vec2D vel;
    int state = UNDEF_INT; // 1 if the wizard is holding a Snaffle, 0 otherwise

    // Entity() = delete;

    static Entity read(istream& istr) {
        // auto ret = Entity();
        int entity_id_, state_;
        float pos_x, pos_y, vel_x, vel_y;
        string type_str;

        istr >> entity_id_ >> type_str >> pos_x >> pos_y >> vel_x >> vel_y
             >> state_;
        istr.ignore();

        Point2D pos{pos_x, pos_y};
        Vec2D vel{vel_x, vel_y};

        Entity ret {entity_id_, from_str(type_str), pos, vel, state_};
        return ret;
    }
};


struct GameState {
    int my_team_id = UNDEF_INT; // if 0 you need to score on the right of the map, if 1 you need to score on the left
    int my_score = UNDEF_INT;
    int my_magic = UNDEF_INT;
    int opponent_score = UNDEF_INT;
    int opponent_magic = UNDEF_INT;
    vector<Entity> wizard;
    vector<Entity> opp_wiz;
    vector<Entity> snaffle;
    vector<Entity> bludger;

    void read_init(istream& istr) {
        istr >> my_team_id; istr.ignore();
    }
    void read_turn(istream& istr) {
        istr >> my_score >> my_magic; istr.ignore();
        istr >> opponent_score >> opponent_magic; istr.ignore();

        int n_entities;
        istr >> n_entities; istr.ignore();

        wizard.clear();
        wizard.reserve(2);
        opp_wiz.clear();
        opp_wiz.reserve(2);
        snaffle.clear();
        snaffle.reserve(7);
        bludger.clear();

        for (int i = 0; i < n_entities; i++) {
            auto entity = Entity::read(istr);
            switch (entity.entity_type) {
                case EntityT::WIZ:
                    wizard.push_back(entity);
                    break;
                case EntityT::OPP:
                    opp_wiz.push_back(entity);
                    break;
                case EntityT::SNF:
                    snaffle.push_back(entity);
                    break;
                case EntityT::BLG:
                    bludger.push_back(entity);
                    break;
                case EntityT::UNDEF:
                    throw GameException("This can't happen");
            }
        }
    }
};


auto closest_snaffle_idx(const GameState& gs, const Point2D& p) -> int {
    auto ret = UNDEF_INT;
    auto closest_distance = numeric_limits<float>::infinity();
    for (int i=0; i < gs.snaffle.size(); ++i) {
        const auto& snf = gs.snaffle[i];
        auto dist = snf.pos.distance_to(p);
        if (dist < closest_distance) {
            ret = i;
            closest_distance = dist;
        }
    }
    return ret;
}


auto value_v1(const GameState& gs) -> float {
    float ret = 0.;

    auto my_goal = (gs.my_team_id == 0 ? GOAL_0 : GOAL_1);
    if (gs.my_team_id == 0) {
        for(const auto& snf : gs.snaffle) {
            auto dist = snf.pos.distance_to(my_goal);
            auto dist_inc = 100.0f / (1.0f + dist / 1000.0f);
            ret += dist_inc;

            const auto vec_to_goal_unit = (my_goal - snf.pos).unit();
            auto vel_comp = snf.vel.dot(vec_to_goal_unit);

            // cerr << "snaffle value incs: " << dist_inc << " vel_comp: " << vel_comp << endl;
            ret += vel_comp;
        }

        for(const auto& wiz:  gs.wizard) {
            for(const auto& snf : gs.snaffle) {
                auto dist = wiz.pos.distance_to(snf.pos);
                ret += 30.0f / (1.0f + dist / 1000.0f);
            }
        }
    } else {
        throw GameException("Pending deal with other team id");
    }
    return ret;
}

struct Move {
    int wiz_idx;
    Vec2D vec;
    float thrust ;

    Move(int wi_, const Vec2D& vec_, float thrust_) : wiz_idx(wi_), vec(vec_), thrust(thrust_) {}

    void emit(ostream& ostr) const {
        ostr << "MOVE" << " "
             << int(vec.dx) << " " << int(vec.dy) << " " << int(thrust) << endl;
    }
};

struct Throw {
    int wiz_idx;
    Vec2D vec;
    float pow = nanf("");

    Throw(int wi_, const Vec2D& vec_, float pow_) : wiz_idx(wi_), vec(vec_), pow(pow_) {}

    void emit(ostream& ostr) const {
        ostr << "THROW" << " "
             << int(vec.dx) << " " << int(vec.dy) << " " << int(pow) << endl;
    }
};


typedef variant<Move, Throw> Action;

auto emit(ostream& ostr, const Action& action) {
    if(holds_alternative<Move>(action)) {
        get<Move>(action).emit(ostr);
    } else {
        get<Throw>(action).emit(ostr);
    }
}


auto simulate_move(GameState& gs, const Move& m) -> void {
    auto& wiz = gs.wizard[m.wiz_idx];
    wiz.vel += (FORCE_TO_DELTA_VEL * m.thrust) * m.vec;
    wiz.pos += (VEL_TO_DELTA_POS * wiz.vel);
}

auto simulate_throw(GameState& gs, const Throw& m) -> void {
    const auto& wiz = gs.wizard[m.wiz_idx];

    auto snf_idx = closest_snaffle_idx(gs, wiz.pos);

    if (snf_idx != UNDEF_INT) {
        auto snf = gs.snaffle[snf_idx];
        snf.vel += m.vec * (FORCE_TO_DELTA_VEL * m.pow);
        snf.pos += snf.vel * VEL_TO_DELTA_POS;
    }
}

constexpr int N_SIMS = 10;

auto simulate_action(const GameState& gs_, const Action& a) -> GameState {
    GameState gs(gs_);

    for(int i=0; i< N_SIMS; ++i) {
        if (holds_alternative<Move>(a)) {
            simulate_move(gs, get<Move>(a));
        } else {
            simulate_throw(gs, get<Throw>(a));
        }
    }
    return gs;
}

auto generate_random_moves(int n, int wiz_idx, const GameState& gs, Rng& mt) -> vector<Action>  {
    vector<Action> ret;
    ret.reserve(n);

    // auto dist_x = uniform_real_distribution<float>(-FIELD_CTR_X, FIELD_CTR_X);
    // auto dist_y = uniform_real_distribution<float>(-FIELD_CTR_Y, FIELD_CTR_Y);
    auto dist_t = uniform_real_distribution<float>(MAX_WIZ_THRUST * 0.7, MAX_WIZ_THRUST);
    auto dist_i = uniform_int_distribution<size_t>(0, gs.snaffle.size());

    // const auto& wiz = gs.wizard[wiz_idx];

    for(int i=0; i < n; ++i) {
        // auto dx = clip(wiz.pos.x + dist_x(mt), 0., FIELD_MAX_X);
        // auto dy = clip(wiz.pos.y + dist_y(mt), 0., FIELD_MAX_Y);
        auto thrust = dist_t(mt);
        const auto& snf = gs.snaffle[dist_i(mt)];
        auto dx = snf.pos.x;
        auto dy = snf.pos.y;
        Vec2D vec { dx, dy };
        Move m{wiz_idx, vec, thrust};
        ret.emplace_back(m);
    }

    return ret;
}


auto generate_random_throws(int n, int wiz_idx, const GameState& gs, Rng& mt) -> vector<Action> {
    vector<Action> ret;
    ret.reserve(n);

    auto dist_x = uniform_real_distribution<float>(-FIELD_CTR_X, FIELD_CTR_X);
    auto dist_y = uniform_real_distribution<float>(-FIELD_CTR_Y, FIELD_CTR_Y);
    auto dist_p = uniform_real_distribution<float>(MAX_THROW_POW / 2.f, MAX_THROW_POW);

    const auto& wiz = gs.wizard[wiz_idx];

    for(int i=0; i < n; ++i) {
        auto dx = clip( wiz.pos.x + dist_x(mt), 0., FIELD_MAX_X);
        auto dy = clip( wiz.pos.y + dist_y(mt), 0., FIELD_MAX_Y);
        auto pow = dist_p(mt);
        Vec2D vec { dx, dy };
        Throw m{wiz_idx, vec, pow};
        ret.emplace_back(m);
    }

    return ret;
}

template<typename Container, typename Fn>
auto argmax(const Container& c, Fn && key) -> decltype(*std::begin(c))
{
    if ( std::begin(c) == std::end(c) )
        throw std::invalid_argument("empty container is not allowed.");

    typedef decltype(*std::begin(c)) V;
    auto cmp = [&](V a, V b){ return key(a) < key(b); };
    return *std::max_element(std::begin(c), std::end(c), cmp);
}


template<typename ElemA, typename Fn>
auto vec_transform(const vector<ElemA>& a, Fn&& fun) -> vector<decltype(fun(a[0]))> {
    // typedef decltype(fun(a[0]) R;
    auto ret = vector<decltype(fun(a[0]))>();
    ret.reserve(a.size());
    for(const auto& elem_a : a) {
        ret.emplace_back(fun(elem_a));
    }
    return ret;
}

template<typename ElemA, typename Fn>
auto vec_argmax(const vector<ElemA>& vec, Fn&& fun) -> int {

    if(vec.size() == 0) {
        throw GameException("Can't take argmax of empty vec");
    }

    int ret = 0;
    float best_value = numeric_limits<float>::min();
    for(int i=0; i < vec.size(); ++i) {
        const auto& elem = vec[i];
        float elem_value = fun(elem);
        if (elem_value > best_value) {
            best_value = elem_value;
            ret = i;
        }
    }
    return ret;
}

auto choose_best_action(const GameState& gs, int wiz_idx, Rng& mt) -> Action {
    int n = 10;

    const auto& wiz = gs.wizard[wiz_idx];

    auto actions = ( wiz.state ?
            generate_random_throws(n, wiz_idx, gs, mt)
            : generate_random_moves(n, wiz_idx, gs, mt));

    auto best_idx = vec_argmax(
            actions,
            [&gs](const Action& a) -> float {
                auto new_gs = simulate_action(gs, a);
                return value_v1(new_gs);
            });

    return actions[best_idx];
}


int main()
{
    cerr << "Starting main" << endl;
    // srand((unsigned) time(NULL));
    std::random_device rd;
    auto mt = Rng(rd());

    auto gs = GameState();
    gs.read_init(cin);

    // game loop
    bool go_on = true;
    while (go_on) {
        gs.read_turn(cin);

        auto val = value_v1(gs);
        cerr << "value_v1: " << val << endl;

        for (int i = 0; i < 2; i++) {
            // Write an action using cout. DON'T FORGET THE "<< endl"
            // To debug: cerr << "Debug messages..." << endl;
            // Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
            // i.e.: "MOVE x y thrust" or "THROW x y power"
            // cout << "MOVE 8000 3750 100" << endl;
            auto action = choose_best_action(gs, i, mt);
            emit(cout, action);
        }
    }
}
