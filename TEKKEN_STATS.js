const TEKKEN_CHARS = [
    'Akuma', 'Alisa', 'Asuka', 'Bob', 'Bryan', 'Claudio', 'Devil Jin', 'Dragunov', 'Eddy', 'Eliza', 'Feng', 'Geese', 'Gigas', 'Heihachi', 'Hwoarang'
    , 'Jack-7', 'Jin', 'Josie', 'Katarina', 'Kazumi', 'Kazuya', 'King', 'Kuma', 'Lars', 'Law', 'Lee', 'Lei', 'Leo', 'Lili', 'Lucky Chloe', 'Master Raven'
    , 'Miguel', 'Nina', 'Noctis', 'Paul', 'Shaheen', 'Steve', 'Xiaoyu', 'Yoshimitsu']


    export default function TekkenStatsApp() {

        const [matches, setMatches] = useState(() => {;
            const savedMatches = localStorage.getItem('tekkenMatches');
            return saveMatches ? JSON.parse(saveMatches) : [];

    });

    const [newMatch, setNewMatch] = useState({
        player1: TEKKEN_CHARS[0],
        player2: TEKKEN_CHARS[1],
        winner: 'player1',
    });

    const [view, setView] = useState("stats");
    const [filter, setFilter] = useState('');

    useEffect(() => {
        localStorage.setItem('tekkenMatches', JSON.stringify(matches));
    }, [matches]);
    
    
    const addMatch = () => {
        const matchData = {
            id: Date.now()
            player1: newMatch.player1,
            player2: newMatch.player2,
            winner: newMatch.winner === 'player1' : newMatch.player1 : newMatch.player2,
            date: new Date().toISOString()
        };
    
        setMatches((..matches, matchData));
        setNewMatch({
            player1: TEKKEN_CHARS[0],
            player2: TEKKEN_CHARS[1],
            winner: 'player1',
        });
    };


    const clearData = () => {
        if (window.confirm("tem certeza que deseja apagar os dados?"))
            setMatches([]);
        }
    };

    const calculateStats = () => {
        const stats = {};


        TEKKEN_CHARS.forEach(char => {
            stats[char] = { wins: 0, matches: 0, usage: 0 };
        });


        matches.forEach(match => {
            stats[match.player1].usage++;
            stats[match.player2].usage++;

            stats[match.player1].matches++;
            stats[match.player2].matches++;

            stats[match.winner].wins++;
        });

        Object.keys(stats).forEach(char => {
            stats[char].winRate = stats(char).matches > 0
            ? ((stats[char].wins / stats[char].matches) * 100).toFixed(1)
            : "0";
        });

        return stats;
    };


    const calculateMatchups = (character) => {
        const matchups = {};

        TEKKEN_CHARS.forEach(char => {
            if (char !== character) {
                matchups[char] = {wins: 0, losses: 0, matches: 0};
            }
        });


        matches.forEach(match => {
            if(match.player1 === character && match.player2 !== character) {
                matchups[match.player2].matches++;
                if (match.winner === character) {
                    matchups[match.player2].wins++;
                } else {;
                }
            }
            else if (match.player2 === character && match.players1 !== character) {
                matchups[match.player1].matches++;
                if (match.winner === character) {
                    matchups[match.player2].wins++;
                } else {
                    matchups[match.player1].losses++;
                }
            }
        });
        
        
        Object.keys(matchups).forEach(opponent => {
            matchups[opponent].winRate = matchups[opponent].matches > 0
            ? ((matchups[opponent].wins / matchups[opponent].matches)* 100).toFixed(1)
            : "0";
        });

        return matchups;
        };

        const stats = calculateStats();


        const StatsView = () => {
            const filteredChars = TEKKEN_CHARS.filter(char =>
                char.toLowerCase().includes(filter.toLowerCase())
            ).sort((a, b) => stats[b].usage - stats[a].usage);


            return (
                <div className="space-y-4">
                    <input
                    type="text"
                    placeholder="Filtrar personagens..."
                    className="w-full p-2 border rounded"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}

                    />


                    <div className="overflow-x-auto">
                        <table className="min-w-full bg-white">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="p-2 text-left">Personagem</th>
                                    <th className="p-2 text-right">Vitórias</th>
                                    <th className="p-2 text-right">Partidas</th>
                                    <th className="p-2 text-right">Winrate</th>
                                    <th className="p-2 text-right">Uso</th>
                                    <th className="p-2 text-center">Detalhes</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredChars.map(char => (
                                    <tr key={char} className="border-t hover:bg-gray-50">
                                        <td className="p-2">{char}</td>
                                        <td className="p-2 text-right">{stats[char].wins}</td>
                                        <td className="p-2 text-right">{stats[char].matches}</td>
                                        <td className="p-2 text-right">{stats[char].winRate}</td>
                                        <td className="p-2 text-right">{stats[char].usage}</td>
                                        <td className="p-2 text center">
                                            <button 
                                                className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                                                onClick={() => {
                                                    setFilter(char);
                                                    setView('matchups');
                                                }}
                                            >
                                             matchups
                                            </button>
                                        </td> 
                                        </tr>
                                        ))}
                                    </tbody>
                                    </table>
                                </div>

                                {matches.length === 0 && (
                                    <div className="text-center p-4 bg-yellow-50 border border-yello2-100 rounded">
                                        Nenhum dado registrado. Lute uma partida primeiro!
                                    </div>
                                )}
                            </div>
                        );
                    };


          const MatchupsView = () => {
            if(!filter) {
                return (
                    <div className="text-center p-4">
                        Selecione um personagem para ver seus matchups.
                    </div>
                );
            }


            const character = TEKKEN_CHARS.find(
                char => char.toLowerCase() === filter.toLowerCase()
            ) || filter;

            const matchups = calculateMatchups(character);

            const sortedOpponents = Object.keys(matchups).sort((a, b) => {
                const matchDiff = matchups[b].matches - matchups[a].matches;
                if (matchDiff !== 0) return matchDiff;

                return a.localeCompare(b);
            });


            return (
                <div className="space-y-4">
                    <div className="flex items-center mb-4">
                        <button
                        className="mr-2 p-1 bg-gray-200 rounded hover:bg-gray-300"
                        onClick={() => {
                            setFilter('');
                            setView('stats');
                        }}
                    >
                          ← Voltar
                        </button>
                        <h2 className="text-xl font-bold">Matchups para {character}</h2>

                    </div>

                    <div className="overflow-x-auto">
                        <table className="min-w-full bg-white">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="p-2 text-left">Oponente</th>
                                    <th className="p-2 text-right">Vitórias</th>
                                    <th className="p-2 text-right">Derrotas</th>
                                    <th className="p-2 text-right">Total</th>
                                    <th className="p-2 text-right">Winrate</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sortedOpponents.map(opponent => {
                                    <tr key={opponent} className="border-t hover:bg-gray-50">
                                        <td className="p-2">{opponent}</td>
                                        <td className="p-2 text-right">{matchups[opponent].wins}</td>
                                        <td className="p-2 text-right">{matchups[opponent].losses}</td>
                                        <td className="p-2 text-right">{matchups[opponent].matches}</td>
                                        <td className="p-2 text-right">{matchups[opponent].winRate}%</td>

                                    </tr>
                                })}

                            </tbody>
                        </table>
                    </div>
                    {sortedOpponents.length === 0 && (
                        <div className="text-center p-4 bg-yellow-50 border border-yellow-100 rounded">
                            Nenhum matchup encontrado para {character}.
                        </div>
                    )}
                </div>
            );
          };
          
        const addMatchView = () => {
            return (
                <div className="space-y-4 max-w-md mx-auto p-4 bg-white rounded shadow">
                    <h2 className="text-xl font-bold">Adicionar nova Partida</h2>
                    <div>
                        <label className="block mb-1">Player 1:</label>
                        <select
                        className="w-full p-2 border rounded"
                        value={newMatch.player1}
                        onChange={(e) => setNewMatch({ ...newMatch, player1: e.target.value })}
                        >
                            {TEKKEN_CHARS.map(char => (
                                <option key={`p1-${char}`} value={char}>{char}</option>
                            ))}
                        </select>
                    </div>
                </div>
            
                
            )
        }                                                
                                        
   